from flask import Blueprint, jsonify, request
from API.models import Client, db
from API.auth import token_required, admin_required

clients_blueprint = Blueprint('clients', __name__)


# Route pour obtenir tous les clients
@clients_blueprint.route('/customers', methods=['GET'])
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


# Route pour obtenir un client spécifique par ID
@clients_blueprint.route('/customers/<int:id>', methods=['GET'])
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


# Route pour créer un nouveau client (admin uniquement)
@clients_blueprint.route('/customers', methods=['POST'])
@token_required
@admin_required
def create_client():
    data = request.json
    if not data or not all(key in data for key in ('nom', 'prenom', 'email')):
        return jsonify({'message': 'Missing data'}), 400

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

    return jsonify({
        "id": new_client.id,
        "nom": new_client.nom,
        "prenom": new_client.prenom,
        "email": new_client.email
    }), 201


# Route pour mettre à jour un client existant (admin uniquement)
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

        return jsonify({
            "id": client.id,
            "nom": client.nom,
            "prenom": client.prenom,
            "email": client.email
        })
    return jsonify({'message': 'Client not found'}), 404


# Route pour supprimer un client (admin uniquement)
@clients_blueprint.route('/customers/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_client(id):
    client = Client.query.get(id)
    if client:
        db.session.delete(client)
        db.session.commit()
        return jsonify({'message': 'Client deleted'}), 200
    return jsonify({'message': 'Client not found'}), 404
