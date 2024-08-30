import unittest
import requests

# URL de base de l'API
BASE_URL = "http://127.0.0.1:5000"

class TestCustomerService(unittest.TestCase):

    def setUp(self):
        # Tentative de connexion et récupération du token
        response = requests.post(f"{BASE_URL}/login", json={
            "username": "admin",
            "password": "admin"
        })
        self.assertEqual(response.status_code, 200)
        self.token = response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_get_customers(self):
        # Test pour récupérer la liste des clients
        response = requests.get(f"{BASE_URL}/customers", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_create_customer(self):
        # Test pour créer un nouveau client
        new_customer = {
            "name": "Client Test",
            "email": "client.test@example.com"
        }
        response = requests.post(f"{BASE_URL}/customers", json=new_customer, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())

    def test_get_single_customer(self):
        # Créer un client pour tester la récupération d'un client spécifique
        new_customer = {
            "name": "Client Unique",
            "email": "client.unique@example.com"
        }
        response = requests.post(f"{BASE_URL}/customers", json=new_customer, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        customer_id = response.json().get("id")

        # Test pour récupérer ce client spécifique
        response = requests.get(f"{BASE_URL}/customers/{customer_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("id"), customer_id)

    def test_update_customer(self):
        # Créer un client pour tester la mise à jour
        new_customer = {
            "name": "Client À Mettre à Jour",
            "email": "client.update@example.com"
        }
        response = requests.post(f"{BASE_URL}/customers", json=new_customer, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        customer_id = response.json().get("id")

        # Test pour mettre à jour le client
        updated_customer = {
            "name": "Client Mis à Jour",
            "email": "client.updated@example.com"
        }
        response = requests.put(f"{BASE_URL}/customers/{customer_id}", json=updated_customer, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("name"), "Client Mis à Jour")

    def test_delete_customer(self):
        # Créer un client pour tester la suppression
        new_customer = {
            "name": "Client À Supprimer",
            "email": "client.delete@example.com"
        }
        response = requests.post(f"{BASE_URL}/customers", json=new_customer, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        customer_id = response.json().get("id")

        # Test pour supprimer ce client
        response = requests.delete(f"{BASE_URL}/customers/{customer_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("message"), "Client supprimé")

        # Vérifier que le client a bien été supprimé
        response = requests.get(f"{BASE_URL}/customers/{customer_id}", headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_logout(self):
        # Test pour se déconnecter et invalider le token
        response = requests.post(f"{BASE_URL}/logout", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("msg"), "Déconnecté avec succès")

        # Vérifier que le token est invalide après déconnexion
        response = requests.get(f"{BASE_URL}/customers", headers=self.headers)
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
