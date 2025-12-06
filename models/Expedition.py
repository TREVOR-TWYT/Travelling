from app import db

class Expedition(db.Model):
    __tablename__ = "expedition"

    num_expedition = db.Column(db.String(20), primary_key=True)
    date_expedition = db.Column(db.DateTime, nullable=False)
    frais = db.Column(db.Integer, nullable=False)
    nature = db.Column(db.String(100))

    id_client_expediteur = db.Column(db.Integer, db.ForeignKey("client.id_client"))
    id_voyage = db.Column(db.Integer, db.ForeignKey("voyage.id_voyage"))

    colis = db.relationship("Colis", backref="expedition", lazy=True)
