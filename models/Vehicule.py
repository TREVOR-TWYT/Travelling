from app import db

class Vehicule(db.Model):
    __tablename__ = "vehicule"

    immatriculation = db.Column(db.String(20), primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    capacite = db.Column(db.Integer, nullable=False)
    statut = db.Column(db.String(50), nullable=False, default="En service")

    voyages = db.relationship("Voyage", backref="vehicule", lazy=True)
