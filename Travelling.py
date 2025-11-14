from sqlalchemy import (
    Column, Integer, String, Date, Time, ForeignKey,
    TIMESTAMP, CheckConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

# -----------------------------------------
#  DATABASE CONNECTION
# -----------------------------------------

# Pour PostgreSQL normal (synchrone)
DATABASE_URL = "postgresql://trevor:TREFRIED1707@localhost/Travelling"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)


# =====================================================
#                    MODELS
# =====================================================

class Agence(Base):
    __tablename__ = "agence"

    id_agence = Column(Integer, primary_key=True, autoincrement=True)
    nom_agence = Column(String(100), nullable=False)
    adresse = Column(String(255))

    personnels = relationship("Personnel", back_populates="agence")
    voyages = relationship("Voyage", back_populates="agence")


class Personnel(Base):
    __tablename__ = "personnel"

    id_personnel = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50))
    role = Column(String(50), nullable=False)
    id_agence = Column(Integer, ForeignKey("agence.id_agence"))

    agence = relationship("Agence", back_populates="personnels")
    voyages = relationship("Voyage", secondary="voyage_personnel", back_populates="personnels")
    colis_traite = relationship("Colis", back_populates="personnel_traiteur")


class Client(Base):
    __tablename__ = "client"

    id_client = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50))
    telephone = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    cni = Column(String(50))

    reservations = relationship("Reservation", back_populates="client")
    expeditions = relationship("Expedition", back_populates="client")


class Trajet(Base):
    __tablename__ = "trajet"

    id_trajet = Column(Integer, primary_key=True, autoincrement=True)
    ville_depart = Column(String(100), nullable=False)
    ville_arrivee = Column(String(100), nullable=False)
    tarif_standard = Column(Integer, nullable=False)
    tarif_vip = Column(Integer, nullable=False)

    voyages = relationship("Voyage", back_populates="trajet")


class Vehicule(Base):
    __tablename__ = "vehicule"

    immatriculation = Column(String(20), primary_key=True)
    type = Column(String(50), nullable=False)
    capacite = Column(Integer, nullable=False)
    statut = Column(String(50), nullable=False, default="En service")

    voyages = relationship("Voyage", back_populates="vehicule")


class Voyage(Base):
    __tablename__ = "voyage"

    id_voyage = Column(Integer, primary_key=True, autoincrement=True)
    date_depart = Column(Date, nullable=False)
    heure_depart = Column(Time, nullable=False)
    id_trajet = Column(Integer, ForeignKey("trajet.id_trajet"), nullable=False)
    immatriculation = Column(String(20), ForeignKey("vehicule.immatriculation"), nullable=False)
    id_agence = Column(Integer, ForeignKey("agence.id_agence"))
    standing = Column(String(50), nullable=False)
    places_reservees = Column(Integer)

    trajet = relationship("Trajet", back_populates="voyages")
    vehicule = relationship("Vehicule", back_populates="voyages")
    agence = relationship("Agence", back_populates="voyages")

    personnels = relationship("Personnel", secondary="voyage_personnel", back_populates="voyages")
    reservations = relationship("Reservation", back_populates="voyage")
    expeditions = relationship("Expedition", back_populates="voyage")


class VoyagePersonnel(Base):
    __tablename__ = "voyage_personnel"

    id_voyage = Column(Integer, ForeignKey("voyage.id_voyage", ondelete="CASCADE"), primary_key=True)
    id_personnel = Column(Integer, ForeignKey("personnel.id_personnel"), primary_key=True)


class Paiement(Base):
    __tablename__ = "paiement"

    id_paiement = Column(Integer, primary_key=True, autoincrement=True)
    montant = Column(Integer, nullable=False)
    date_paiement = Column(TIMESTAMP, nullable=False)
    mode = Column(String(50), nullable=False)
    reference_transaction = Column(String(100), unique=True, nullable=False)

    reservation = relationship("Reservation", back_populates="paiement", uselist=False)


class Reservation(Base):
    __tablename__ = "reservation"

    num_reservation = Column(String(20), primary_key=True)
    date_reservation = Column(TIMESTAMP, nullable=False)
    statut = Column(String(50), nullable=False)

    id_client = Column(Integer, ForeignKey("client.id_client"), nullable=False)
    id_voyage = Column(Integer, ForeignKey("voyage.id_voyage"), nullable=False)
    id_paiement = Column(Integer, ForeignKey("paiement.id_paiement"), unique=True)

    client = relationship("Client", back_populates="reservations")
    voyage = relationship("Voyage", back_populates="reservations")
    paiement = relationship("Paiement", back_populates="reservation")


class Expedition(Base):
    __tablename__ = "expedition"

    num_expedition = Column(String(20), primary_key=True)
    date_expedition = Column(TIMESTAMP, nullable=False)
    frais = Column(Integer, nullable=False)
    nature = Column(String(100))

    id_client_expediteur = Column(Integer, ForeignKey("client.id_client"))
    id_voyage = Column(Integer, ForeignKey("voyage.id_voyage"))

    client = relationship("Client", back_populates="expeditions")
    voyage = relationship("Voyage", back_populates="expeditions")
    colis = relationship("Colis", back_populates="expedition")


class Colis(Base):
    __tablename__ = "colis"

    id_colis = Column(Integer, primary_key=True, autoincrement=True)
    num_expedition = Column(String(20), ForeignKey("expedition.num_expedition"), nullable=False)
    nature = Column(String(100), nullable=False)
    quantite = Column(Integer, nullable=False)

    id_personnel_traiteur = Column(Integer, ForeignKey("personnel.id_personnel"))

    expedition = relationship("Expedition", back_populates="colis")
    personnel_traiteur = relationship("Personnel", back_populates="colis_traite")


# =====================================================
#  CREATE TABLES
# =====================================================

def create_database():
    Base.metadata.create_all(engine)
