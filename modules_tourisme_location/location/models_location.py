from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Vehicule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marque = db.Column(db.String(100), nullable=False)
    modele = db.Column(db.String(100), nullable=False)
    prix_jour = db.Column(db.Float, nullable=False)
