from app import db

class Voyage(db.Model):
    __tablename__ = "voyage"

    id_voyage = db.Column(db.Integer, primary_key=True)
    date_depart = db.Column(db.Date, nullable=False)
    heure_depart = db.Column(db.Time, nullable=False)
    
    id_trajet = db.Column(db.Integer, db.ForeignKey("trajet.id_trajet"), nullable=False)
    immatriculation = db.Column(db.String(20), db.ForeignKey("vehicule.immatriculation"), nullable=False)
    id_agence = db.Column(db.Integer, db.ForeignKey("agence.id_agence"))
    
    standing = db.Column(db.String(50), nullable=False)
    places_reservees = db.Column(db.Integer)

    personnels = db.relationship("VoyagePersonnel", backref="voyage", cascade="all, delete", lazy=True)
    reservations = db.relationship("Reservation", backref="voyage", lazy=True)
    expeditions = db.relationship("Expedition", backref="voyage", lazy=True)
