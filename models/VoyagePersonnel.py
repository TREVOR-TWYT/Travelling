from app import db

class VoyagePersonnel(db.Model):
    __tablename__ = "voyage_personnel"

    id_voyage = db.Column(db.Integer, db.ForeignKey("voyage.id_voyage"), primary_key=True)
    id_personnel = db.Column(db.Integer, db.ForeignKey("personnel.id_personnel"), primary_key=True)
