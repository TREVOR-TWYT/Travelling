from app import db

class Paiement(db.Model):
    __tablename__ = "paiement"

    id_paiement = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Integer, nullable=False)
    date_paiement = db.Column(db.DateTime, nullable=False)
    mode = db.Column(db.String(50), nullable=False)
    reference_transaction = db.Column(db.String(100), unique=True, nullable=False)

    reservation = db.relationship("Reservation", backref="paiement", uselist=False)
