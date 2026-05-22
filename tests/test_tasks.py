from app.extensions import db
from app.models import Notification
from app.tasks import process_notification

def test_process_notification_success(app):
    with app.app_context():
        notification = Notification(
            type="email",
            recipient="test@example.com",
            message="Test message",
            status="pending"
        )
        db.session.add(notification)
        db.session.commit()
        
        notif_id = notification.id

        process_notification(notif_id)

        updated_notification = Notification.query.get(notif_id)
        assert updated_notification.status == "sent"
        assert updated_notification.error_text is None

def test_process_notification_invalid_type(app):
    with app.app_context():
        notification = Notification(
            type="invalid_type",
            recipient="test",
            message="Test",
            status="pending"
        )
        db.session.add(notification)
        db.session.commit()
        
        notif_id = notification.id

        process_notification(notif_id)

        updated_notification = Notification.query.get(notif_id)
        assert updated_notification.status == "failed"
        assert "Unsupported notification type" in updated_notification.error_text
