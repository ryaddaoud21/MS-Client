import pytest
from API.models import db

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    with app.app_context():
        db.create_all()
    yield db
    with app.app_context():
        db.drop_all()