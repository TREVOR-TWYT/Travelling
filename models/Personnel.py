from app import db

class Personnel(db.Model):
    __tablename__ = "personnel"

    id_personnel = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50))
    role = db.Column(db.String(50), nullable=False)
    id_agence = db.Column(db.Integer, db.ForeignKey("agence.id_agence"))

    voyages_affectes = db.relationship(
        "VoyagePersonnel",
        backref="personnel",
        cascade="all, delete",
        lazy=True
    )
