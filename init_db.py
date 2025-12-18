#from app import app, db
from models import *
from werkzeug.security import generate_password_hash
from datetime import datetime, date, time, timedelta
import random

def init_database():
    """Initialiser la base de données avec des données de test enrichies"""
    with app.app_context():
        print("🔄 Initialisation de la base de données...")
        
        # 1. Créer toutes les tables
        db.create_all()
        print("✅ Tables créées")
        
        # --- DONNÉES DE BASE ---
        
        # Admin
        if not Admin.query.first():
            admin = Admin(
                nom="admin",
                email = "admin@gmail.com",
                password_hash=generate_password_hash("1234")
            )
            db.session.add(admin)
            print("✅ Compte admin créé (login: admin / password: 1234)")
        
        # Agences
        if Agence.query.count() == 0:
            agences_data = [
                Agence(nom_agence="Agence Yaoundé Centre", adresse="Centre-ville, Yaoundé"),
                Agence(nom_agence="Agence Douala Akwa", adresse="Akwa, Douala"),
                Agence(nom_agence="Agence Bamenda Commercial", adresse="Commercial Avenue, Bamenda"),
            ]
            for agence in agences_data:
                db.session.add(agence)
            print("✅ Agences créées")
        
        # Trajets
        if Trajet.query.count() == 0:
            trajets_data = [
                Trajet(ville_depart="Douala", ville_arrivee="Yaoundé", tarif_standard=8000, tarif_vip=12000),
                Trajet(ville_depart="Yaoundé", ville_arrivee="Bamenda", tarif_standard=10000, tarif_vip=15000),
                Trajet(ville_depart="Douala", ville_arrivee="Bafoussam", tarif_standard=7000, tarif_vip=10000),
                Trajet(ville_depart="Yaoundé", ville_arrivee="Douala", tarif_standard=8000, tarif_vip=12000),
                Trajet(ville_depart="Bamenda", ville_arrivee="Bafoussam", tarif_standard=6000, tarif_vip=9000),
                Trajet(ville_depart="Kribi", ville_arrivee="Douala", tarif_standard=7000, tarif_vip=10000),
            ]
            for trajet in trajets_data:
                db.session.add(trajet)
            print("✅ Trajets créés")
        
        # Véhicules
        if Vehicule.query.count() == 0:
            vehicules_data = [
                Vehicule(immatriculation="LT-0001-YA", type="Bus Standard", capacite=40, statut="En service"),
                Vehicule(immatriculation="LT-0002-YA", type="Bus VIP", capacite=30, statut="En service"),
                Vehicule(immatriculation="LT-0003-DLA", type="Bus Standard", capacite=40, statut="En service"),
                Vehicule(immatriculation="LT-0004-DLA", type="Bus VIP", capacite=30, statut="En maintenance"),
                Vehicule(immatriculation="CE-5555-DLA", type="Mini VIP", capacite=15, statut="En service"),
                Vehicule(immatriculation="CE-6666-YA", type="Mini Standard", capacite=20, statut="En service"),
            ]
            for vehicule in vehicules_data:
                db.session.add(vehicule)
            print("✅ Véhicules créés")
        
        db.session.commit() # Commit initial pour que les FK soient valides

        # --- DONNÉES ENRICHIES ---

        # 2. Clients (10)
        if Client.query.count() == 0:
            clients_data = [
                {"nom": "Tchoukoua", "prenom": "Alain", "tel": "677112233", "email": "alain.t@test.com", "cni": "111111111", "mdp": "pass1"},
                {"nom": "Nguene", "prenom": "Brenda", "tel": "699887766", "email": "brenda.n@test.com", "cni": "222222222", "mdp": "pass2"},
                {"nom": "Fotsing", "prenom": "Charles", "tel": "655443322", "email": "charles.f@test.com", "cni": "333333333", "mdp": "pass3"},
                {"nom": "Mbarga", "prenom": "Diane", "tel": "670102030", "email": "diane.m@test.com", "cni": "444444444", "mdp": "pass4"},
                {"nom": "Ekani", "prenom": "Eric", "tel": "688990011", "email": "eric.e@test.com", "cni": "555555555", "mdp": "pass5"},
                {"nom": "Ndjama", "prenom": "Fanny", "tel": "671234567", "email": "fanny.n@test.com", "cni": "666666666", "mdp": "pass6"},
                {"nom": "Tanga", "prenom": "Guy", "tel": "690123012", "email": "guy.t@test.com", "cni": "777777777", "mdp": "pass7"},
                {"nom": "Nana", "prenom": "Hélène", "tel": "650505050", "email": "helene.n@test.com", "cni": "888888888", "mdp": "pass8"},
                {"nom": "Kemajou", "prenom": "Igor", "tel": "678901234", "email": "igor.k@test.com", "cni": "999999999", "mdp": "pass9"},
                {"nom": "Njoh", "prenom": "Julie", "tel": "698765432", "email": "julie.n@test.com", "cni": "000000000", "mdp": "pass10"},
            ]
            for client_data in clients_data:
                client = Client(
                    nom=client_data["nom"],
                    prenom=client_data["prenom"],
                    telephone=client_data["tel"],
                    email=client_data["email"],
                    cni=client_data["cni"],
                    password_hash=generate_password_hash(client_data["mdp"]) # Utilisez hash
                )
                db.session.add(client)
            print("✅ 10 Clients créés")

        # 3. Voyages (12)
        if Voyage.query.count() == 0:
            trajets = Trajet.query.all()
            vehicules = Vehicule.query.filter_by(statut="En service").all()
            agences = Agence.query.all()
            
            voyages_list = []
            base_date = date.today() + timedelta(days=random.randint(1, 5))
            heures = [time(6, 30), time(8, 0), time(12, 0), time(16, 0)]
            
            for i in range(12):
                trajet = random.choice(trajets)
                vehicule = random.choice(vehicules)
                agence = random.choice(agences)
                heure_depart = random.choice(heures)
                
                # Assure un mélange Standard/VIP
                standing = "VIP" if vehicule.type.endswith("VIP") else "Standard"

                voyage = Voyage(
                    date_depart=base_date + timedelta(days=i // 4), # 4 voyages par jour
                    heure_depart=heure_depart,
                    id_trajet=trajet.id_trajet,
                    immatriculation=vehicule.immatriculation,
                    id_agence=agence.id_agence,
                    standing=standing,
                    places_reservees=0 # Sera mis à jour par les réservations
                )
                voyages_list.append(voyage)
                db.session.add(voyage)

            print("✅ 12 Voyages créés")
            db.session.commit() # Commit pour avoir les IDs de voyage

        # 4. Réservations (Multiples)
        if Reservation.query.count() == 0:
            clients = Client.query.all()
            voyages_actifs = Voyage.query.all()
            
            for i in range(25): # Créer 25 réservations de test
                client = random.choice(clients)
                voyage = random.choice(voyages_actifs)
                
                montant = voyage.trajet.tarif_vip if voyage.standing == "VIP" else voyage.trajet.tarif_standard
                mode_paiement = random.choice(['Mobile Money', 'Carte Bancaire', 'Espèces'])
                
                # Créer le paiement
                paiement = Paiement(
                    montant=montant,
                    date_paiement=datetime.now() - timedelta(minutes=random.randint(1, 100)),
                    mode=mode_paiement,
                    reference_transaction=f"TRANS-{random.randint(1000000, 9999999)}"
                )
                db.session.add(paiement)
                db.session.flush() # Assure que l'ID de paiement est généré
                
                # Créer la réservation
                reservation = Reservation(
                    num_reservation=f"RES-{random.randint(10000, 99999)}",
                    date_reservation=datetime.now() - timedelta(minutes=random.randint(10, 150)),
                    statut=random.choice(['Confirmée', 'En attente', 'Annulée']),
                    id_client=client.id_client,
                    id_voyage=voyage.id_voyage,
                    id_paiement=paiement.id_paiement
                )
                db.session.add(reservation)
                
                # Mise à jour des places réservées (simple, sans gestion de la capacité maximale ici)
                if reservation.statut == 'Confirmée':
                    voyage.places_reservees += 1
                    db.session.add(voyage)
            
            print("✅ 25 Réservations et Paiements créés")
            
        # --- COMMIT FINAL ---
        db.session.commit()
        
        print("=" * 50)
        print("🎉 Base de données initialisée avec succès!")
        print("=" * 50)
        print("📋 Identifiants admin pour test:")
        print("   Username: admin")
        print("   Password: 1234")
        print("=" * 50)
        print("🌐 Accès application: http://localhost:5000")
        print("🔐 Accès admin: http://localhost:5000/admin-login")
        print("=" * 50)

if __name__ == "__main__":
    init_database()