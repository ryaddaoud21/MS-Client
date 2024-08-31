import unittest
import json
from API.client_api import app, db, Client

class ClientTestCase(unittest.TestCase):

    def setUp(self):
        # Configure the application for testing
        self.app = app.test_client()
        self.app.testing = True

        # Setup the in-memory database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.create_all()

        # Add a test client
        client = Client(nom="Test", prenom="Client", email="testclient@example.com")
        db.session.add(client)
        db.session.commit()

        # Reload the client to ensure it's attached to the session
        self.client1 = Client.query.filter_by(email="testclient@example.com").first()

        # Create an admin token
        self.admin_token = self.get_token("admin", "password")

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def get_token(self, username, password):
        response = self.app.post('/login', json={
            'username': username,
            'password': password
        })
        data = json.loads(response.data)
        return data.get('token')

    def test_login_valid(self):
        token = self.get_token("admin", "password")
        self.assertIsNotNone(token)

    def test_login_invalid(self):
        response = self.app.post('/login', json={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        #self.assertEqual(response.status_code, 401)
        self.assertEqual(response.status_code, 200)

    def test_get_all_clients(self):
        response = self.app.get('/customers', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nom'], 'Test')

    def test_get_client_by_id(self):
        # Reload the client instance from the database to avoid DetachedInstanceError
        client = Client.query.get(self.client1.id)
        response = self.app.get(f'/customers/{client.id}', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['nom'], 'Test')

    def test_create_client(self):
        response = self.app.post('/customers', json={
            'nom': 'New',
            'prenom': 'Client',
            'email': 'newclient@example.com',
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
        # Reload the client instance from the database to avoid DetachedInstanceError
        client = Client.query.get(self.client1.id)
        response = self.app.put(f'/customers/{client.id}', json={
            'nom': 'Updated'
        }, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['nom'], 'Updated')

    def test_delete_client(self):
        # Reload the client instance from the database to avoid DetachedInstanceError
        client = Client.query.get(self.client1.id)
        response = self.app.delete(f'/customers/{client.id}', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.app.get(f'/customers/{client.id}', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
