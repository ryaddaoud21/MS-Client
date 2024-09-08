from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from API.models import db, Client

# Création du blueprint pour les routes des clients
clients_blueprint = Blueprint('clients', __name__)

# Route pour obtenir tous les clients (GET)
@clients_blueprint.route('/customers', methods=['GET'])
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
    } for c in clients]), 200

# Route pour obtenir un client par ID (GET)
@clients_blueprint.route('/customers/<int:id>', methods=['GET'])
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
def create_client():
    data = request.json
    if not data or not all(key in data for key in ['nom', 'prenom', 'email']):
        return jsonify({'message': 'Nom, prénom, et email sont obligatoires'}), 400

    new_client = Client(
        nom=data['nom'],
        prenom=data['prenom'],
        email=data['email'],
        telephone=data.get('telephone'),
        adresse=data.get('adresse'),
        ville=data.get('ville'),
        code_postal=data.get('code_postal'),
        pays=data.get('pays')
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({"id": new_client.id, "nom": new_client.nom, "prenom": new_client.prenom}), 201

# Route pour mettre à jour un client par ID (PUT)
@clients_blueprint.route('/customers/<int:id>', methods=['PUT'])
def update_client(id):
    client = Client.query.get(id)
    if not client:
        return jsonify({'message': 'Client not found'}), 404

    data = request.json

    # Mise à jour des champs du client
    client.nom = data.get('nom', client.nom)
    client.prenom = data.get('prenom', client.prenom)
    client.email = data.get('email', client.email)
    client.telephone = data.get('telephone', client.telephone)
    client.adresse = data.get('adresse', client.adresse)
    client.ville = data.get('ville', client.ville)
    client.code_postal = data.get('code_postal', client.code_postal)
    client.pays = data.get('pays', client.pays)

    try:
        db.session.commit()
        return jsonify({"id": client.id, "nom": client.nom, "prenom": client.prenom, "email": client.email}), 200
    except IntegrityError as e:
        db.session.rollback()  # Annuler la transaction en cours
        return jsonify({"error": "Integrity error: " + str(e.orig)}), 400



# Route pour supprimer un client par ID (DELETE)
@clients_blueprint.route('/customers/<int:id>', methods=['DELETE'])
def delete_client(id):
    client = Client.query.get(id)
    if not client:
        return jsonify({'message': 'Client not found'}), 404

    try:
        db.session.delete(client)
        db.session.commit()
        return jsonify({'message': 'Client deleted successfully'}), 200
    except IntegrityError:
        db.session.rollback()  # Annuler la transaction en cours
        return jsonify({'message': 'Cannot delete client. There are associated orders.'}), 400