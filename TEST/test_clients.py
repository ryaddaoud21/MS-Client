'''
import pytest
from flask import Flask
from API.models import db, Client
from API.clients import clients_blueprint
from API.auth import auth_blueprint
from API.config import Config

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de données en mémoire pour les tests
    app.config['TESTING'] = True

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(clients_blueprint)
    app.register_blueprint(auth_blueprint)

    yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_token(client):
    # Simulation d'un token pour l'admin
    response = client.post('/login', json={'username': 'admin', 'password': 'password'})
    return response.json['token']

@pytest.fixture
def user_token(client):
    # Simulation d'un token pour un utilisateur non admin
    response = client.post('/login', json={'username': 'user1', 'password': 'userpass'})
    return response.json['token']

# Test pour récupérer tous les clients
def test_get_clients(client, admin_token):
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/customers', headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)

# Test pour créer un client
def test_create_client(client, admin_token):
    client_data = {
        "nom": "Doe",
        "prenom": "John",
        "email": "johndoe@example.com",
        "telephone": "1234567890",
        "adresse": "123 Rue Exemple",
        "ville": "Paris",
        "code_postal": "75000",
        "pays": "France"
    }
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.post('/customers', json=client_data, headers=headers)
    assert response.status_code == 201
    assert 'id' in response.json

# Test de mise à jour d'un client
def test_update_client(client, admin_token):
    client_data = {
        "nom": "Doe",
        "prenom": "John",
        "email": "johndoe@example.com",
        "telephone": "1234567890",
        "adresse": "123 Rue Exemple",
        "ville": "Paris",
        "code_postal": "75000",
        "pays": "France"
    }
    headers = {'Authorization': f'Bearer {admin_token}'}
    create_response = client.post('/customers', json=client_data, headers=headers)

    updated_data = {
        "nom": "Smith",
        "prenom": "John"
    }

    client_id = create_response.json['id']
    response = client.put(f'/customers/{client_id}', json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json['nom'] == "Smith"
    assert response.json['id'] == client_id

# Test de suppression d'un client
def test_delete_client(client, admin_token):
    client_data = {
        "nom": "Doe",
        "prenom": "John",
        "email": "johndoe@example.com",
        "telephone": "1234567890",
        "adresse": "123 Rue Exemple",
        "ville": "Paris",
        "code_postal": "75000",
        "pays": "France"
    }
    headers = {'Authorization': f'Bearer {admin_token}'}
    create_response = client.post('/customers', json=client_data, headers=headers)

    client_id = create_response.json['id']
    delete_response = client.delete(f'/customers/{client_id}', headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json['message'] == 'Client deleted successfully'

# Test de tentative de suppression d'un client par un utilisateur non admin
def test_delete_client_non_admin(client, admin_token, user_token):
    # Créer le client en tant qu'administrateur
    client_data = {
        "nom": "Doe",
        "prenom": "John",
        "email": "johndoe@example.com",
        "telephone": "1234567890",
        "adresse": "123 Rue Exemple",
        "ville": "Paris",
        "code_postal": "75000",
        "pays": "France"
    }
    headers_admin = {'Authorization': f'Bearer {admin_token}'}
    create_response = client.post('/customers', json=client_data, headers=headers_admin)

    # Vérifier que le client a bien été créé
    client_id = create_response.json.get('id', None)
    assert client_id is not None, "Client ID should exist"

    # Essayer de supprimer le client avec un utilisateur non administrateur
    headers_user = {'Authorization': f'Bearer {user_token}'}
    delete_response = client.delete(f'/customers/{client_id}', headers=headers_user)

    # Vérifier que la suppression est refusée
    assert delete_response.status_code == 403
    assert delete_response.json['error'] == 'Forbidden'
'''