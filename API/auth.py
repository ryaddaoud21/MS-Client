from flask import Blueprint, jsonify, request, make_response
import secrets
from functools import wraps

auth_blueprint = Blueprint('auth', __name__)

# Simulated token storage (for simplicity)
valid_tokens = {}


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


# Endpoint for user login
@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not 'username' in data or not 'password' in data:
        return jsonify({"msg": "Username and password required"}), 400

    # Liste d'utilisateurs fictifs
    users = {
        "admin": {"password": "password", "role": "admin"},
        "user1": {"password": "userpass", "role": "user"}
    }

    if data['username'] in users and users[data['username']]['password'] == data['password']:
        token = generate_token()
        valid_tokens[data['username']] = {"token": token, "role": users[data['username']]['role']}
        return jsonify({"token": token}), 200

    return jsonify({"msg": "Invalid credentials"}), 401


# Endpoint for user logout
@auth_blueprint.route('/logout', methods=['POST'])
@token_required
def logout():
    token = request.headers.get('Authorization').split('Bearer ')[1]
    user = next((u for u, t in valid_tokens.items() if t["token"] == token), None)

    if user:
        del valid_tokens[user]
        return jsonify({"msg": "Successfully logged out"}), 200

    return make_response(jsonify({"error": "Unauthorized"}), 401)


# Example protected route for admins
@auth_blueprint.route('/admin-only', methods=['GET'])
@token_required
@admin_required
def admin_only():
    return jsonify({"msg": "Welcome, admin!"}), 200


@auth_blueprint.route('/', methods=['GET'])
def index():
    return jsonify({"msg": "Welcome to the API. The service is up and running!"}), 200
