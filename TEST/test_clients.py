
import pytest
from flask import Flask
from API.clients import clients_blueprint
from API.models import db, Client
from API.config import Config

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de données en mémoire pour les tests
    app.config['TESTING'] = True

    db.init_app(app)

    # Enregistrez les blueprints
    app.register_blueprint(clients_blueprint, url_prefix='/')

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture
def client_data():
    return {
        "nom": "Doe",
        "prenom": "John",
        "email": "johndoe@example.com",
        "telephone": "1234567890",
        "adresse": "123 Rue Exemple",
        "ville": "Paris",
        "code_postal": "75000",
        "pays": "France"
    }

def test_get_clients(client):
    response = client.get('/customers')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_client(client, client_data):
    response = client.post('/customers', json=client_data)
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['nom'] == client_data['nom']
    assert response.json['prenom'] == client_data['prenom']

def test_update_client(client, client_data):
    # Créez d'abord un client pour le mettre à jour
    client.post('/customers', json=client_data)
    updated_data = {"nom": "Smith", "prenom": "John"}

    response = client.put('/customers/1', json=updated_data)
    assert response.status_code == 200
    assert response.json['nom'] == "Smith"

def test_delete_client(client, client_data):
    # Créez un client pour le supprimer
    client.post('/customers', json=client_data)

    response = client.delete('/customers/1')
    assert response.status_code == 200
    assert response.json['message'] == "Client deleted successfully"

def test_update_nonexistent_client(client):
    updated_data = {"nom": "Smith"}
    response = client.put('/customers/999', json=updated_data)
    assert response.status_code == 404
    assert response.json['message'] == "Client not found"

def test_delete_nonexistent_client(client):
    response = client.delete('/customers/999')
    assert response.status_code == 404
    assert response.json['message'] == "Client not found"
