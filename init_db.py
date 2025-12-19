from app import app, db
from models import *
from werkzeug.security import generate_password_hash
from datetime import datetime, date, time, timedelta
import random
import uuid

def init_database():
    """Initialisation totale : Agences, Trajets, Flotte, Personnel, Sites, Clients, Réservations, Logistique et Locations"""
    with app.app_context():
        print("🔄 Nettoyage et création des tables...")
        db.drop_all()
        db.create_all()

        # --- 1. ADMINISTRATEUR ---
        admin = Admin(
            nom="Administrateur", 
            email="admin@gmail.com", 
            password_hash=generate_password_hash("1234")
        )
        db.session.add(admin)

        # --- 2. AGENCES ---
        print("🏢 Création des agences...")
        agences = [
            Agence(nom_agence="Agence Yaoundé Centre", adresse="Centre-ville, Yaoundé"),
            Agence(nom_agence="Agence Douala Akwa", adresse="Akwa, Douala"),
            Agence(nom_agence="Agence Bamenda Commercial", adresse="Commercial Avenue, Bamenda"),
            Agence(nom_agence="Agence Kribi Plage", adresse="Débarcadère, Kribi"),
            Agence(nom_agence="Agence Bafoussam", adresse="Marché Central, Bafoussam")
        ]
        db.session.add_all(agences)
        db.session.commit()

        # --- 3. TRAJETS ---
        print("🛣️ Création des trajets...")
        trajets = [
            Trajet(ville_depart="Douala", ville_arrivee="Yaoundé", tarif_standard=8000, tarif_vip=12000),
            Trajet(ville_depart="Yaoundé", ville_arrivee="Bamenda", tarif_standard=10000, tarif_vip=15000),
            Trajet(ville_depart="Douala", ville_arrivee="Bafoussam", tarif_standard=7000, tarif_vip=10000),
            Trajet(ville_depart="Kribi", ville_arrivee="Douala", tarif_standard=7000, tarif_vip=10000)
        ]
        db.session.add_all(trajets)
        db.session.commit()

        # --- 4. VÉHICULES (Bus + SUV pour location) ---
        print("🚍 Création de la flotte...")
        bus_list = []
        for i in range(10):
            v = Vehicule(immatriculation=f"LT-{100+i}-MT", type=random.choice(["Bus VIP", "Bus Standard"]), capacite=random.choice([30, 70]), statut="En service")
            bus_list.append(v)
            db.session.add(v)
        
        suv_list = []
        for i, nom in enumerate(["Toyota Prado", "Toyota Hilux", "Suzuki Swift", "Mitsubishi Pajero", "Range Rover"]):
            v = Vehicule(immatriculation=f"CE-{500+i}-LOC", type=nom, capacite=5, statut="En service")
            suv_list.append(v)
            db.session.add(v)
        db.session.commit()

        # --- 5. PERSONNEL (Utilisation de 'role' selon ton model) ---
        print("👨‍💼 Création du personnel...")
        for i in range(15):
            p = Personnel(
                nom=random.choice(["Etoundi", "Kamga", "Moussa", "Nguene"]),
                prenom=random.choice(["Samuel", "Fanny", "Eric", "Brenda"]),
                role=random.choice(["Chauffeur", "Hôtesse", "Guichetier", "Agent"]),
                id_agence=random.choice(agences).id_agence
            )
            db.session.add(p)

        # --- 6. SITES TOURISTIQUES ---
        print("📸 Création des sites...")
        sites_data = [
                    SiteTouristique(nom_site="Chutes de la Lobé", ville="Kribi", region="Sud", description="Les chutes se jetant dans l'océan.", tarif_adulte=2000, tarif_enfant=1000, image_url="Chute de la lobé.jpeg"),
                    SiteTouristique(nom_site="Parc de Waza", ville="Waza", region="Extrême-Nord", description="Safari et lions en plein Sahel.", tarif_adulte=5000, tarif_enfant=2500, image_url="waza.jpeg"),
                    SiteTouristique(nom_site="Mont Cameroun", ville="Buea", region="Sud-Ouest", description="Le char des dieux.", tarif_adulte=3000, tarif_enfant=1500, image_url="mont_fako.jpeg"),
                    SiteTouristique(nom_site="Réserve du Dja", ville="Lomié", region="Est", description="Biodiversité forêt équatoriale.", tarif_adulte=4000, tarif_enfant=2000, image_url="dja.jpg"),
                    SiteTouristique(nom_site="Palais de Foumban", ville="Foumban", region="Ouest", description="Siège du Sultanat Bamoun.", tarif_adulte=1500, tarif_enfant=750, image_url="foumban.jpg"),
                    SiteTouristique(nom_site="Falaise de Dschang", ville="Dschang", region="Ouest", description="Site montagneux de la ville de Dschang.", tarif_adulte=1500, tarif_enfant=750, image_url="falaise_dschang.jpg")
                ]
        db.session.add_all(sites_data)
        db.session.commit()

        # --- 7. CLIENTS (Tes 10 clients officiels) ---
        print("👥 Création de tes 10 clients...")
        clients_data = [
            ("Tchoukoua", "Alain", "677112233", "alain.t@test.com", "pass1"),
            ("Nguene", "Brenda", "699887766", "brenda.n@test.com", "pass2"),
            ("Fotsing", "Charles", "655443322", "charles.f@test.com", "pass3"),
            ("Mbarga", "Diane", "670102030", "diane.m@test.com", "pass4"),
            ("Ekani", "Eric", "688990011", "eric.e@test.com", "pass5"),
            ("Ndjama", "Fanny", "671234567", "fanny.n@test.com", "pass6"),
            ("Tanga", "Guy", "690123012", "guy.t@test.com", "pass7"),
            ("Nana", "Hélène", "650505050", "helene.n@test.com", "pass8"),
            ("Kemajou", "Igor", "678901234", "igor.k@test.com", "pass9"),
            ("Njoh", "Julie", "698765432", "julie.n@test.com", "pass10")
        ]
        created_clients = []
        for nom, pre, tel, em, mdp in clients_data:
            c = Client(nom=nom, prenom=pre, telephone=tel, email=em, password_hash=generate_password_hash(mdp))
            created_clients.append(c)
            db.session.add(c)
        db.session.commit()

        # --- 8. VOYAGES ET RÉSERVATIONS ---
        print("🎫 Création des voyages et des tickets...")
        for i in range(10):
            v = Voyage(
                date_depart=date.today() + timedelta(days=i),
                heure_depart=time(random.choice([6, 8, 12, 21]), 0),
                id_trajet=random.choice(trajets).id_trajet,
                immatriculation=random.choice(bus_list).immatriculation,
                id_agence=random.choice(agences).id_agence,
                standing=random.choice(["VIP", "Standard"]),
                places_reservees=0
            )
            db.session.add(v)
            db.session.flush() # Pour avoir l'id_voyage tout de suite

            # Créer 2 réservations par voyage
            for _ in range(2):
                c = random.choice(created_clients)
                pay = Paiement(montant=8000, date_paiement=datetime.now(), mode="Mobile Money", reference_transaction=f"TXN-{uuid.uuid4().hex[:8].upper()}")
                db.session.add(pay)
                db.session.flush()
                res = Reservation(num_reservation=f"RES-{uuid.uuid4().hex[:6].upper()}", date_reservation=datetime.now(), statut="Confirmée", id_client=c.id_client, id_voyage=v.id_voyage, id_paiement=pay.id_paiement)
                v.places_reservees += 1
                db.session.add(res)

        # --- 9. EXPÉDITIONS ET COLIS (Logistique) ---
        print("📦 Création des expéditions de colis...")
        for i in range(10):
            c = random.choice(created_clients)
            exp = Expedition(
                num_expedition=f"EXP-MBOA-{2000+i}",
                date_expedition=datetime.now(),
                frais=random.randint(2000, 5000),
                nature=random.choice(["Vivres", "Documents", "Électronique"]),
                id_client_expediteur=c.id_client
            )
            db.session.add(exp)
            db.session.flush()
            
            # Détails du colis et suivi
            db.session.add(Colis(num_expedition=exp.num_expedition, nature=exp.nature, quantite=1))
            db.session.add(StatutColis(num_expedition=exp.num_expedition, statut='Expédié', date_heure=datetime.now(), localisation="Agence de Départ"))
        db.session.commit()
# --- 10. LOCATIONS DE VÉHICULES ---
        print("🚗 Création des contrats de location SUV...")
        for i in range(len(suv_list)):
            # On récupère le client et le véhicule pour cette itération
            c = created_clients[i]
            vehicule_a_louer = suv_list[i]
            
            loc = LocationVehicule(
                num_location=f"LOC-{uuid.uuid4().hex[:6].upper()}",
                date_debut=date.today(),
                date_fin=date.today() + timedelta(days=2),
                heure_debut=time(8, 0),
                immatriculation=vehicule_a_louer.immatriculation,
                id_client=c.id_client,
                tarif_journalier=35000,
                caution=100000,
                montant_total=70000,
                statut="En cours"
            )
            db.session.add(loc)
            
            # 🔥 SYNCHRONISATION : On marque le véhicule comme loué dans la base
            vehicule_a_louer.statut = "Loué"

        db.session.commit()

        db.session.commit()
        print("\n" + "="*60 + "\n✅ TOUTES LES DONNÉES ONT ÉTÉ RESTAURÉES AVEC SUCCÈS !\n" + "="*60)

if __name__ == "__main__":
    init_database()