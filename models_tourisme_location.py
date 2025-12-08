from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# -----------------
# Module Client
# -----------------
class Client(db.Model):
    __tablename__ = 'client'
    id_client = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(50))
    cni = db.Column(db.String(20))
    
    # Relation vers Location
    locations = db.relationship(
        'Location', backref='client', cascade="all, delete-orphan"
    )

# -----------------
# Module Vehicule
# -----------------
class Vehicule(db.Model):
    __tablename__ = 'vehicule'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    marque = db.Column(db.String(50))
    
    # Relation vers Location
    locations = db.relationship(
        'Location', backref='vehicule', cascade="all, delete-orphan"
    )

# -----------------
# Module Location
# -----------------
class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer, db.ForeignKey('client.id_client'), nullable=False
    )
    vehicule_id = db.Column(
        db.Integer, db.ForeignKey('vehicule.id'), nullable=False
    )
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    prix_total = db.Column(db.Float)
    statut = db.Column(db.String(20), default="En cours")

# -----------------
# Module Agence
# -----------------
class Agence(db.Model):
    __tablename__ = 'agence'
    id_agence = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    adresse = db.Column(db.String(100))
    
    # Relation vers Tourisme
    tours = db.relationship(
        'Tourisme', backref='agence', cascade="all, delete-orphan"
    )

# -----------------
# Module Tourisme
# -----------------
class Tourisme(db.Model):
    __tablename__ = 'tourisme'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duree = db.Column(db.String(50))  # ex: "3 jours"
    prix = db.Column(db.Float)
    agence_id = db.Column(db.Integer, db.ForeignKey('agence.id_agence'))

