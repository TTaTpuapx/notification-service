import logging
from app.extensions import db
from app.models import Notification

logger = logging.getLogger(__name__)

def send_email(recipient, subject, message):
    logger.info(f"Simulating EMAIL to {recipient} | Subject: {subject} | Message: {message}")
    return True

def send_telegram(recipient, message):
    logger.info(f"Simulating TELEGRAM to {recipient} | Message: {message}")
    return True

def send_sms(recipient, message):
    logger.info(f"Simulating SMS to {recipient} | Message: {message}")
    return True

def process_notification(notification_id):
    from app import create_app
    app = create_app()
    
    with app.app_context():
        notification = Notification.query.get(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found in database")
            return

        logger.info(f"Processing notification {notification_id}, type={notification.type}")

        try:
            if notification.type == 'email':
                send_email(notification.recipient, notification.subject, notification.message)
            elif notification.type == 'telegram':
                send_telegram(notification.recipient, notification.message)
            elif notification.type == 'sms':
                send_sms(notification.recipient, notification.message)
            else:
                raise ValueError(f"Unsupported notification type: {notification.type}")

            notification.status = 'sent'
            notification.error_text = None
            logger.info(f"Notification {notification_id} sent successfully")
            
        except Exception as e:
            notification.status = 'failed'
            notification.error_text = str(e)
            logger.exception(f"Failed to send notification {notification_id}: {e}")
        db.session.commit()
