from app import db

class Trajet(db.Model):
    __tablename__ = "trajet"

    id_trajet = db.Column(db.Integer, primary_key=True)
    ville_depart = db.Column(db.String(100), nullable=False)
    ville_arrivee = db.Column(db.String(100), nullable=False)
    tarif_standard = db.Column(db.Integer, nullable=False)
    tarif_vip = db.Column(db.Integer, nullable=False)

    voyages = db.relationship("Voyage", backref="trajet", lazy=True)
