from flask import Flask, jsonify, request
from .models import db, Client  # Import du modèle Client et de SQLAlchemy
from .auth import token_required, admin_required
from .config import Config  # Import de la configuration
from .rabbitmq_consumer import start_consumer_in_thread  # Import du consommateur RabbitMQ

# Initialisation de l'application Flask
app = Flask(__name__)

# Chargement de la configuration
app.config.from_object(Config)

# Lier SQLAlchemy à l'application
db.init_app(app)

# Endpoint pour récupérer tous les clients
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

# Endpoint pour récupérer un client spécifique par ID
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
    return jsonify({'message': 'Client non trouvé'}), 404

# Endpoint pour créer un nouveau client (administrateur seulement)
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

# Endpoint pour mettre à jour un client existant (administrateur seulement)
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
    return jsonify({'message': 'Client non trouvé'}), 404

# Endpoint pour supprimer un client (administrateur seulement)
@app.route('/customers/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def delete_client(id):
    client = Client.query.get(id)
    if client:
        db.session.delete(client)
        db.session.commit()
        return jsonify({'message': 'Client supprimé'})
    return jsonify({'message': 'Client non trouvé'}), 404

if __name__ == '__main__':
    # Démarrer le consommateur RabbitMQ dans un thread séparé
    start_consumer_in_thread()

    # Lancer le serveur Flask
    app.run(host='0.0.0.0', port=5001)
