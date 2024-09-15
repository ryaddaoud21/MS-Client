from flask import Blueprint, jsonify, request, make_response
import secrets
from functools import wraps
from flask import request, jsonify, make_response
from API.services.rabbitmq_consumer import verify_token
auth_blueprint = Blueprint('auth', __name__)

# Simulated token storage (for simplicity)
valid_tokens = {}

def token_required(f):
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return make_response(jsonify({"error": "Unauthorized"}), 401)

        received_token = token.split('Bearer ')[1]
        authenticated, role = verify_token(received_token)

        if not authenticated:
            return make_response(jsonify({"error": "Unauthorized"}), 401)

        request.role = role
        return f(*args, **kwargs)

    return decorated_function

@auth_blueprint.route('/', methods=['GET'])
def index():
    return jsonify({"msg": "Welcome to the CUSTOMER's API. The service is up and running!"}), 200
