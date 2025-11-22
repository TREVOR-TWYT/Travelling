from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Agence(db.Model):
    __tablename__ = "agence"

    id_agence = db.Column(db.Integer, primary_key=True)
    nom_agence = db.Column(db.String(100), nullable=False)
    adresse = db.Column(db.String(255))

    personnels = db.relationship("Personnel", back_populates="agence")
    voyages = db.relationship("Voyage", back_populates="agence")


class Personnel(db.Model):
    __tablename__ = "personnel"

    id_personnel = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50))
    role = db.Column(db.String(50), nullable=False)
    id_agence = db.Column(db.Integer, db.ForeignKey("agence.id_agence"))

    agence = db.relationship("Agence", back_populates="personnels")
    voyages = db.relationship(
        "Voyage", secondary="voyage_personnel", back_populates="personnels"
    )
    colis_traite = db.relationship("Colis", back_populates="personnel_traiteur")


class Client(db.Model):
    __tablename__ = "client"

    id_client = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50))
    telephone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    cni = db.Column(db.String(50))
    password = db.Column(db.String(255), nullable=False)


    reservations = db.relationship("Reservation", back_populates="client")
    expeditions = db.relationship("Expedition", back_populates="client")


class Trajet(db.Model):
    __tablename__ = "trajet"

    id_trajet = db.Column(db.Integer, primary_key=True)
    ville_depart = db.Column(db.String(100), nullable=False)
    ville_arrivee = db.Column(db.String(100), nullable=False)
    tarif_standard = db.Column(db.Integer, nullable=False)
    tarif_vip = db.Column(db.Integer, nullable=False)

    voyages = db.relationship("Voyage", back_populates="trajet")


class Vehicule(db.Model):
    __tablename__ = "vehicule"

    immatriculation = db.Column(db.String(20), primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    capacite = db.Column(db.Integer, nullable=False)
    statut = db.Column(db.String(50), nullable=False, default="En service")

    voyages = db.relationship("Voyage", back_populates="vehicule")


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

    trajet = db.relationship("Trajet", back_populates="voyages")
    vehicule = db.relationship("Vehicule", back_populates="voyages")
    agence = db.relationship("Agence", back_populates="voyages")

    personnels = db.relationship(
        "Personnel", secondary="voyage_personnel", back_populates="voyages"
    )
    reservations = db.relationship("Reservation", back_populates="voyage")
    expeditions = db.relationship("Expedition", back_populates="voyage")


class VoyagePersonnel(db.Model):
    __tablename__ = "voyage_personnel"

    id_voyage = db.Column(db.Integer, db.ForeignKey("voyage.id_voyage", ondelete="CASCADE"), primary_key=True)
    id_personnel = db.Column(db.Integer, db.ForeignKey("personnel.id_personnel"), primary_key=True)


class Paiement(db.Model):
    __tablename__ = "paiement"

    id_paiement = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Integer, nullable=False)
    date_paiement = db.Column(db.TIMESTAMP, nullable=False)
    mode = db.Column(db.String(50), nullable=False)
    reference_transaction = db.Column(db.String(100), unique=True, nullable=False)

    reservation = db.relationship("Reservation", back_populates="paiement", uselist=False)


class Reservation(db.Model):
    __tablename__ = "reservation"

    num_reservation = db.Column(db.String(20), primary_key=True)
    date_reservation = db.Column(db.TIMESTAMP, nullable=False)
    statut = db.Column(db.String(50), nullable=False)

    id_client = db.Column(db.Integer, db.ForeignKey("client.id_client"), nullable=False)
    id_voyage = db.Column(db.Integer, db.ForeignKey("voyage.id_voyage"), nullable=False)
    id_paiement = db.Column(db.Integer, db.ForeignKey("paiement.id_paiement"), unique=True)

    client = db.relationship("Client", back_populates="reservations")
    voyage = db.relationship("Voyage", back_populates="reservations")
    paiement = db.relationship("Paiement", back_populates="reservation")


class Expedition(db.Model):
    __tablename__ = "expedition"

    num_expedition = db.Column(db.String(20), primary_key=True)
    date_expedition = db.Column(db.TIMESTAMP, nullable=False)
    frais = db.Column(db.Integer, nullable=False)
    nature = db.Column(db.String(100))

    id_client_expediteur = db.Column(db.Integer, db.ForeignKey("client.id_client"))
    id_voyage = db.Column(db.Integer, db.ForeignKey("voyage.id_voyage"))

    client = db.relationship("Client", back_populates="expeditions")
    voyage = db.relationship("Voyage", back_populates="expeditions")
    colis = db.relationship("Colis", back_populates="expedition")


class Colis(db.Model):
    __tablename__ = "colis"

    id_colis = db.Column(db.Integer, primary_key=True)
    num_expedition = db.Column(db.String(20), db.ForeignKey("expedition.num_expedition"), nullable=False)
    nature = db.Column(db.String(100), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    id_personnel_traiteur = db.Column(db.Integer, db.ForeignKey("personnel.id_personnel"))

    expedition = db.relationship("Expedition", back_populates="colis")
    personnel_traiteur = db.relationship("Personnel", back_populates="colis_traite")
