import pytest
from flask import Flask
from API.auth import auth_blueprint
from API.config import Config


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enregistrement du blueprint auth
    app.register_blueprint(auth_blueprint, url_prefix='/')

    return app


@pytest.fixture
def auth_token(client):
    response = client.post('/login', json={'username': 'admin', 'password': 'password'})

    # Ajoutez des logs pour voir la réponse en cas de problème
    assert response.status_code == 200, f"Login failed: {response.data}"
    assert 'token' in response.json, f"No token returned in response: {response.data}"

    return response.json['token']

def test_login(client):
    response = client.post('/login', json={'username': 'admin', 'password': 'password'})
    assert response.status_code == 200
    assert 'token' in response.json

def test_login_fail(client):
    response = client.post('/login', json={'username': 'admin', 'password': 'wrongpassword'})
    assert response.status_code == 401
    assert response.json['msg'] == 'Invalid credentials'


def test_logout(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    logout_response = client.post('/logout', headers=headers)

    assert logout_response.status_code == 200
    assert logout_response.json['msg'] == 'Successfully logged out'

