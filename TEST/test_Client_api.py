import unittest
import json
from API.client_endpoints import app, db  # Import de l'application et de la base de données
from API.models import Client  # Import du modèle Client

class ClientTestCase(unittest.TestCase):

    def setUp(self):
        # Configure l'application pour le test
        self.app = app.test_client()
        self.app.testing = True

        # Réinitialiser la base de données avant chaque test
        with app.app_context():
            db.drop_all()  # Supprimer toutes les tables pour éviter les conflits
            db.create_all()  # Recréer toutes les tables

            # Ajouter un client de test
            client = Client(nom="Test", prenom="Client", email="testclient@example.com")
            db.session.add(client)
            db.session.commit()

            # Recharger le client pour s'assurer qu'il est bien dans la session
            self.client1 = Client.query.filter_by(email="testclient@example.com").first()

            # Créer un token admin pour les tests
            self.admin_token = self.get_token("admin", "password")

    def tearDown(self):
        # Nettoyer la base de données après chaque test
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def get_token(self, username, password):
        # Simuler l'obtention d'un token via l'endpoint /login
        response = self.app.post('/login', json={
            'username': username,
            'password': password
        })
        data = json.loads(response.data)
        return data.get('token')

    def test_login_valid(self):
        # Test de la validité d'un login avec les bonnes informations
        token = self.get_token("admin", "password")
        self.assertIsNotNone(token)

    def test_login_invalid(self):
        # Test d'un login avec des informations incorrectes
        response = self.app.post('/login', json={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)

    def test_get_all_clients(self):
        # Test de l'obtention de tous les clients
        response = self.app.get('/customers', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nom'], 'Test')

    def test_get_client_by_id(self):
        # Test de l'obtention d'un client spécifique par son ID
        client = Client.query.get(self.client1.id)
        response = self.app.get(f'/customers/{client.id}', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['nom'], 'Test')

    def test_create_client(self):
        # Test de la création d'un nouveau client avec un e-mail unique
        response = self.app.post('/customers', json={
            'nom': 'New',
            'prenom': 'Client',
            'email': 'newclient@example.com',  # Utiliser un e-mail unique pour éviter les conflits
            'telephone': '1234567890',
            'adresse': '123 Test St',
            'ville': 'Testville',
            'code_postal': '12345',
            'pays': 'Testland'
        }, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['nom'], 'New')

    def test_update_client(self):
        # Test de la mise à jour d'un client existant
        client = Client.query.get(self.client1.id)
        response = self.app.put(f'/customers/{client.id}', json={
            'nom': 'Updated'
        }, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['nom'], 'Updated')

    def test_delete_client(self):
        # Test de la suppression d'un client existant
        client = Client.query.get(self.client1.id)
        response = self.app.delete(f'/customers/{client.id}', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.app.get(f'/customers/{client.id}', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
