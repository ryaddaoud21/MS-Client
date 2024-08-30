from flask import Flask, jsonify, request, make_response
from functools import wraps
import secrets

app = Flask(__name__)

# Simulation d'un "stockage" des tokens pour cet exemple (en mémoire, à remplacer par une base de données en production)
valid_tokens = {}

# Fonction pour générer un token sécurisé
def generate_token():
    return secrets.token_urlsafe(32)

# Décorateur pour vérifier le token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return make_response(jsonify({"error": "Unauthorized"}), 401)

        received_token = token.split('Bearer ')[1]
        if received_token not in valid_tokens.values():
            return make_response(jsonify({"error": "Unauthorized"}), 401)

        return f(*args, **kwargs)
    return decorated_function

# Mock Database
customers = [
    {"id": 1, "name": "Client 1", "email": "client1@example.com"},
    {"id": 2, "name": "Client 2", "email": "client2@example.com"},
]

# Endpoint pour générer un token d'accès
@app.route('/login', methods=['POST'])
def login():
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        return jsonify({"msg": "Nom d'utilisateur et mot de passe nécessaires"}), 400

    username = request.json['username']
    password = request.json['password']

    # Simple vérification des identifiants
    if username == 'admin' and password == 'admin':
        token = generate_token()
        valid_tokens[username] = token
        return jsonify({"token": token}), 200

    return jsonify({"msg": "Identifiants incorrects"}), 401

# Endpoint pour déconnexion (invalide le token)
@app.route('/logout', methods=['POST'])
@token_required
def logout():
    token = request.headers.get('Authorization').split('Bearer ')[1]
    user = next((u for u, t in valid_tokens.items() if t == token), None)
    if user:
        del valid_tokens[user]
        return jsonify({"msg": "Déconnecté avec succès"}), 200
    return make_response(jsonify({"error": "Unauthorized"}), 401)

# Sécurisation des endpoints avec le décorateur personnalisé @token_required
@app.route('/customers', methods=['GET'])
@token_required
def get_customers():
    return jsonify(customers)

@app.route('/customers/<int:id>', methods=['GET'])
@token_required
def get_customer(id):
    customer = next((c for c in customers if c['id'] == id), None)
    if customer:
        return jsonify(customer)
    return jsonify({'message': 'Client non trouvé'}), 404

@app.route('/customers', methods=['POST'])
@token_required
def create_customer():
    new_customer = request.json
    new_customer['id'] = len(customers) + 1
    customers.append(new_customer)
    return jsonify(new_customer), 201

@app.route('/customers/<int:id>', methods=['PUT'])
@token_required
def update_customer(id):
    customer = next((c for c in customers if c['id'] == id), None)
    if customer:
        data = request.json
        customer.update(data)
        return jsonify(customer)
    return jsonify({'message': 'Client non trouvé'}), 404

@app.route('/customers/<int:id>', methods=['DELETE'])
@token_required
def delete_customer(id):
    customer = next((c for c in customers if c['id'] == id), None)
    if customer:
        customers.remove(customer)
        return jsonify({'message': 'Client supprimé'})
    return jsonify({'message': 'Client non trouvé'}), 404

if __name__ == '__main__':
    app.run(debug=True)
