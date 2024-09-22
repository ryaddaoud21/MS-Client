import json

import pika
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from flask import Flask, jsonify, request, make_response
from API.models import db, Client
from prometheus_client import Counter, Summary, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import multiprocess, CollectorRegistry
from prometheus_client import multiprocess
from API.auth  import token_required,admin_required


# Création du blueprint pour les routes des clients
from API.services.pika_config import get_channel, publish_message

clients_blueprint = Blueprint('clients', __name__)

# Variables pour le monitoring Prometheus
REQUEST_COUNT = Counter('client_requests_total', 'Total number of requests for clients')
REQUEST_LATENCY = Summary('client_processing_seconds', 'Time spent processing client requests')


# Route pour obtenir tous les clients (GET)
@clients_blueprint.route('/customers', methods=['GET'])
@REQUEST_LATENCY.time()
@token_required
def get_clients():
    REQUEST_COUNT.inc()  # Incrémenter le compteur de requêtes
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
    } for c in clients]), 200

# Route pour obtenir un client par ID (GET)
@clients_blueprint.route('/customers/<int:id>', methods=['GET'])
@token_required
def get_client(id):
    client = Client.query.get(id)
    if not client:
        return jsonify({'message': 'Client not found'}), 404

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
    }), 200

# Route pour créer un nouveau client (POST)
@clients_blueprint.route('/customers', methods=['POST'])
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
    return jsonify(
        {"id": new_client.id, "nom": new_client.nom, "prenom": new_client.prenom, "email": new_client.email}), 201


# Route pour mettre à jour un client par ID (PUT)
@clients_blueprint.route('/customers/<int:id>', methods=['PUT'])
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



# Route pour supprimer un client par ID (DELETE)
@clients_blueprint.route('/customers/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_client(id):
    # Récupérer le client par son ID
    client = Client.query.get(id)

    if client:
        # Supprimer le client de la base de données
        db.session.delete(client)
        db.session.commit()

        # Publier un message dans RabbitMQ pour indiquer la suppression du client
        try:
            # Créer le message à envoyer à RabbitMQ
            message = {"client_id": id}
            publish_message('client_deletion_queue', message)  # Utiliser la fonction de publication

        except Exception as e:
            # Gestion des erreurs liées à RabbitMQ
            return jsonify({'message': 'Client deleted, but failed to notify RabbitMQ', 'error': str(e)}), 500

        # Retourner un message de succès après suppression
        return jsonify({'message': 'Client deleted successfully'}), 200

    # Retourner une erreur 404 si le client n'est pas trouvé
    return jsonify({'message': 'Client not found'}), 404