from flask_sqlalchemy import SQLAlchemy

# Initialisation de SQLAlchemy
db = SQLAlchemy()

# Modèle pour la table des clients dans la base de données
class Client(db.Model):
    __tablename__ = 'clients'

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
