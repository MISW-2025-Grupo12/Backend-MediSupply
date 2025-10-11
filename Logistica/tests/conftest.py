import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api import create_app
from src.config.db import db

@pytest.fixture(scope='session')
def app():
    os.environ['TESTING'] = 'True'
    app = create_app()
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def app_context(app):
    with app.app_context():
        yield app
