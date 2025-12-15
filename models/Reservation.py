from app import db

class Reservation(db.Model):
    __tablename__ = "reservation"

    num_reservation = db.Column(db.String(20), primary_key=True)
    date_reservation = db.Column(db.DateTime, nullable=False)
    statut = db.Column(db.String(50), nullable=False)

    id_client = db.Column(db.Integer, db.ForeignKey("client.id_client"), nullable=False)
    id_voyage = db.Column(db.Integer, db.ForeignKey("voyage.id_voyage"), nullable=False)
    id_paiement = db.Column(db.Integer, db.ForeignKey("paiement.id_paiement"), unique=True)

