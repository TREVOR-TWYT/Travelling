from app import db

class Agence(db.Model):
    __tablename__ = "agence"

    id_agence = db.Column(db.Integer, primary_key=True)
    nom_agence = db.Column(db.String(100), nullable=False)
    adresse = db.Column(db.String(255))
    
    personnels = db.relationship("Personnel", backref="agence", lazy=True)
    voyages = db.relationship("Voyage", backref="agence", lazy=True)
