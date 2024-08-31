from flask import Flask, jsonify, request, make_response
from functools import wraps
import secrets
from flask_sqlalchemy import SQLAlchemy

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration de la base de données MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/client_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de SQLAlchemy
db = SQLAlchemy(app)

# Modèle de la base de données pour les clients
class Client(db.Model):
    __tablename__ = 'clients'  # Nom de la table dans MySQL

    id = db.Column('ClientID', db.Integer, primary_key=True)
    nom = db.Column('Nom', db.String(255), nullable=False)
    prenom = db.Column('Prenom', db.String(255), nullable=False)
    email = db.Column('Email', db.String(255), nullable=False, unique=True)
    telephone = db.Column('Telephone', db.String(20))
    adresse = db.Column('Adresse', db.String(255))
    ville = db.Column('Ville', db.String(255))
    code_postal = db.Column('CodePostal', db.String(10))
    pays = db.Column('Pays', db.String(255))

    def __repr__(self):
        return f'<Client {self.nom} {self.prenom}>'

# Simulated token storage (In a real application, use a database or other secure storage)
valid_tokens = {}

# Function to generate a secure token
def generate_token():
    return secrets.token_urlsafe(32)

# Decorator to require a valid token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return make_response(jsonify({"error": "Unauthorized"}), 401)

        received_token = token.split('Bearer ')[1]
        user = next((u for u, t in valid_tokens.items() if t["token"] == received_token), None)

        if not user:
            return make_response(jsonify({"error": "Unauthorized"}), 401)

        request.user = user
        request.role = valid_tokens[user]['role']

        return f(*args, **kwargs)
    return decorated_function

# Decorator to require admin role
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.role != "admin":
            return make_response(jsonify({"error": "Forbidden"}), 403)
        return f(*args, **kwargs)
    return decorated_function

# Endpoint to login and generate a token
@app.route('/login', methods=['POST'])
def login():
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        return jsonify({"msg": "Username and password required"}), 400

    username = request.json['username']
    password = request.json['password']

    # Simple user validation (hardcoded users)
    users = {
        "admin": {"password": "password", "role": "admin"},
        "user1": {"password": "userpass", "role": "user"},
    }

    if username in users and users[username]['password'] == password:
        token = generate_token()
        valid_tokens[username] = {"token": token, "role": users[username]['role']}
        return jsonify({"token": token}), 200

    return jsonify({"msg": "Invalid credentials"}), 401

# Endpoint to logout and invalidate the token
@app.route('/logout', methods=['POST'])
@token_required
def logout():
    token = request.headers.get('Authorization').split('Bearer ')[1]
    user = next((u for u, t in valid_tokens.items() if t["token"] == token), None)
    if user:
        del valid_tokens[user]
        return jsonify({"msg": "Successfully logged out"}), 200
    return make_response(jsonify({"error": "Unauthorized"}), 401)

# Endpoint to get all clients
@app.route('/customers', methods=['GET'])
@token_required
def get_clients():
    clients = Client.query.all()
    return jsonify([{
        "id": c.id,
        "nom": c.nom,
        "prenom": c.prenom,
        "email": c.email,
        "telephone": c.telephone,
        "adresse": c.adresse,
        "ville": c.ville,
        "code_postal": c.code_postal,
        "pays": c.pays
    } for c in clients])

# Endpoint to get a specific client by ID
@app.route('/customers/<int:id>', methods=['GET'])
@token_required
def get_client(id):
    client = Client.query.get(id)
    if client:
        return jsonify({
            "id": client.id,
            "nom": client.nom,
            "prenom": client.prenom,
            "email": client.email,
            "telephone": client.telephone,
            "adresse": client.adresse,
            "ville": client.ville,
            "code_postal": client.code_postal,
            "pays": client.pays
        })
    return jsonify({'message': 'Client not found'}), 404

# Endpoint to create a new client (admin only)
@app.route('/customers', methods=['POST'])
@token_required
@admin_required
def create_client():
    data = request.json
    new_client = Client(
        nom=data['nom'],
        prenom=data['prenom'],
        email=data['email'],
        telephone=data['telephone'],
        adresse=data['adresse'],
        ville=data['ville'],
        code_postal=data['code_postal'],
        pays=data['pays']
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({"id": new_client.id, "nom": new_client.nom, "prenom": new_client.prenom, "email": new_client.email}), 201

# Endpoint to update a client (admin only)
@app.route('/customers/<int:id>', methods=['PUT'])
@token_required
@admin_required
def update_client(id):
    client = Client.query.get(id)
    if client:
        data = request.json
        client.nom = data.get('nom', client.nom)
        client.prenom = data.get('prenom', client.prenom)
        client.email = data.get('email', client.email)
        client.telephone = data.get('telephone', client.telephone)
        client.adresse = data.get('adresse', client.adresse)
        client.ville = data.get('ville', client.ville)
        client.code_postal = data.get('code_postal', client.code_postal)
        client.pays = data.get('pays', client.pays)
        db.session.commit()
        return jsonify({"id": client.id, "nom": client.nom, "prenom": client.prenom, "email": client.email})
    return jsonify({'message': 'Client not found'}), 404

# Endpoint to delete a client (admin only)
@app.route('/customers/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_client(id):
    client = Client.query.get(id)
    if client:
        db.session.delete(client)
        db.session.commit()
        return jsonify({'message': 'Client deleted'})
    return jsonify({'message': 'Client not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
