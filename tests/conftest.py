import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app as flask_app
from models import db

@pytest.fixture(scope='module')
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    with app.test_client() as test_client:
        # Enable session handling by setting TESTING = False (counterintuitively)
        app.config['TESTING'] = False  # This enables sessions
        # Enable preserve_context_on_exception for more reliable session handling
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        # Generate a random but stable secret key for session
        app.config['SECRET_KEY'] = 'test_secret_key'
        
        test_client.testing = True
        yield test_client

@pytest.fixture(scope='function')
def runner(app):
    return app.test_cli_runner()

@pytest.fixture(autouse=True)
def fast_password_hash(monkeypatch):
    from werkzeug import security
    monkeypatch.setattr(security, "generate_password_hash", lambda password, *args, **kwargs: password)
    monkeypatch.setattr(security, "check_password_hash", lambda hash, password: hash == password)
