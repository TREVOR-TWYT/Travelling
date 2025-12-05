from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Tourisme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    prix = db.Column(db.Float, nullable=False)
