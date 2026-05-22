import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
PHONE_REGEX = re.compile(r'^[\+\d\s\-\(\)]+$')

def validate_notification(data):
    errors = {}
    
    required_fields = ['type', 'recipient', 'message']
    for field in required_fields:
        if not data.get(field) or not str(data.get(field)).strip():
            errors[field] = f"{field} is required"

    if errors:
        return errors

    type_ = data['type']
    recipient = data['recipient']

    if type_ not in ['email', 'telegram', 'sms']:
        errors['type'] = "type must be one of: email, telegram, sms"
        return errors

    if type_ == 'email':
        if not EMAIL_REGEX.match(recipient):
            errors['recipient'] = "Invalid email format"
    elif type_ == 'telegram':
        if not (recipient.startswith('@') and len(recipient) > 1) and not PHONE_REGEX.match(recipient):
            errors['recipient'] = "Invalid telegram recipient (must be @username or phone number)"
    elif type_ == 'sms':
        if not PHONE_REGEX.match(recipient):
            errors['recipient'] = "Invalid phone number format"

    return errors
