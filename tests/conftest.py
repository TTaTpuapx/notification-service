import os
import sys
from unittest.mock import MagicMock

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

mock_redis_module = MagicMock()
mock_redis_module.Redis.from_url.return_value = MagicMock()
mock_rq_module = MagicMock()
mock_rq_module.Queue.return_value = MagicMock()
sys.modules['redis'] = mock_redis_module
sys.modules['rq'] = mock_rq_module

import pytest
from app import create_app
from app.extensions import db
import app.api.notifications as notifications_module

@pytest.fixture
def app():
    mock_queue = MagicMock()
    mock_queue.enqueue.return_value = None
    notifications_module.get_queue = lambda: mock_queue

    app_instance = create_app()
    app_instance.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False
    })

    with app_instance.app_context():
        db.create_all()
        yield app_instance
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
