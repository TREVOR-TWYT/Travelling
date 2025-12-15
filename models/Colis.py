from app import db

class Colis(db.Model):
    __tablename__ = "colis"

    id_colis = db.Column(db.Integer, primary_key=True)
    num_expedition = db.Column(db.String(20), db.ForeignKey("expedition.num_expedition"), nullable=False)
    nature = db.Column(db.String(100), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)

    id_personnel_traiteur = db.Column(db.Integer, db.ForeignKey("personnel.id_personnel"))
