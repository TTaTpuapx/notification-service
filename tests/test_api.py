import json

def test_create_notification_success(client):
    payload = {
        "type": "email",
        "recipient": "test@example.com",
        "message": "Hello world"
    }
    response = client.post(
        '/api/v1/notifications', 
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["status"] == "queued"

def test_create_notification_validation_error(client):
    payload = {
        "type": "email",
        "recipient": "not-an-email",
        "message": "Hello"
    }
    response = client.post(
        '/api/v1/notifications', 
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert "recipient" in response.get_json()["errors"]

def test_create_notification_missing_fields(client):
    payload = {
        "type": "email"
    }
    response = client.post(
        '/api/v1/notifications', 
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 400

def test_get_notification_not_found(client):
    response = client.get('/api/v1/notifications/00000000-0000-0000-0000-000000000000')
    assert response.status_code == 404
