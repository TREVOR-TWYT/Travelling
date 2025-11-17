from app import db

class Client(db.Model):
    __tablename__ = "client"

    id_client = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50))
    telephone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    cni = db.Column(db.String(50))

    reservations = db.relationship("Reservation", backref="client", lazy=True)
    expeditions = db.relationship("Expedition", backref="client_expediteur", lazy=True)
