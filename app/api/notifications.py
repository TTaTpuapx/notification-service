from flask import request, jsonify, current_app
from redis import Redis
from rq import Queue

from app.api import bp
from app.extensions import db
from app.models import Notification
from app.api.validators import validate_notification

def get_queue():
    redis_conn = Redis.from_url(current_app.config['REDIS_URL'])
    return Queue('notifications', connection=redis_conn)

@bp.route('/notifications', methods=['POST'])
def create_notification():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400

    errors = validate_notification(data)
    if errors:
        return jsonify({'errors': errors}), 400

    notification = Notification(
        type=data['type'],
        recipient=data['recipient'],
        subject=data.get('subject'),
        message=data['message'],
        status='pending'
    )
    db.session.add(notification)
    db.session.commit()

    queue = get_queue()
    queue.enqueue('app.tasks.process_notification', notification.id)

    current_app.logger.info(
        f"Notification created and queued",
        extra={'notification_id': notification.id, 'type': data['type']}
    )

    return jsonify({
        'id': notification.id,
        'status': 'queued'
    }), 201

@bp.route('/notifications/<notification_id>', methods=['GET'])
def get_notification(notification_id):
    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404

    return jsonify({
        'id': notification.id,
        'status': notification.status,
        'error': notification.error_text
    }), 200

@bp.route('/notifications', methods=['GET'])
def list_notifications():
    status = request.args.get('status')
    limit = request.args.get('limit', default=50, type=int)
    offset = request.args.get('offset', default=0, type=int)

    if limit > 100:
        limit = 100

    query = Notification.query
    if status:
        query = query.filter_by(status=status)

    total = query.count()
    notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()

    return jsonify({
        'total': total,
        'limit': limit,
        'offset': offset,
        'items': [n.to_dict() for n in notifications]
    }), 200
