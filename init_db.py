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
                    SiteTouristique(nom_site="Chutes de la Lobé", ville="Kribi", region="Sud", description="Les chutes de la Lobé se trouvent au sud du Cameroun. Situées à sept kilomètres au sud de Kribi, elles ont la particularité rare au monde du fait que le fleuve Lobé se jette directement dans l'océan Atlantique. Elles constituent l'attraction majeure de Kribi. Cette région comporte de grandes plages de sable fin où viennent pondre deux espèces de tortues marines : la tortue luth et la tortue olivâtre. Le projet de sauvegarde des tortues marines est géré par le Centre spécialisé de recherche sur les écosystèmes marins (CERECOMA) de l'IRAD (Institut de recherche agricole pour le développement) et l'Union mondiale pour la nature (UICN-France ; UICN-BRAC). Ce projet pilote comporte un volet d'aide communautaire aux villages de pêcheurs côtiers, aide actuellement développée à travers un partenariat entre les mairies de Courteranges en France et Campo au Cameroun. Ce partenariat a été couronné par le jumelage des deux mairies en avril 2006. Le CERECOMA est une structure créée en février 2006 par le conseil d'administration de l'IRAD ; il est placé sous l'autorité scientifique de l'IRAD et sous la tutelle du ministère de la Recherche Scientifique et de l'Innovation (MINRESI) du Cameroun. D'autre part, les tortues capturées accidentellement par les pêcheurs artisanaux de Kribi sont parrainées par des hommes d'affaires ou des touristes, ce qui permet de dédommager les pêcheurs et sauver ces tortues qui, sinon, seraient tuées pour leur viande et leur carapace. ", tarif_adulte=2000, tarif_enfant=1000, image_url="Chute de la lobé.jpeg"),
                    SiteTouristique(nom_site="Parc de Waza", ville="Waza", region="Extrême-Nord", description="Le parc national de Waza est l'un des parcs nationaux du Cameroun. Situé dans l'extrême nord du pays, non loin du lac Tchad, près de Waza, il couvre une superficie de 1 700 km2. C'est une réserve de biosphère reconnue par l'Unesco depuis 1979. Riche d'une faune naturelle exceptionnelle, il est l'un des atouts touristiques du Cameroun. D'abord réserve de chasse créée en 1934 sous le nom de Zina-Waza, le parc a reçu le statut de parc national en 1968.", tarif_adulte=5000, tarif_enfant=2500, image_url="waza.jpeg"),
                    SiteTouristique(nom_site="Mont Cameroun", ville="Buea", region="Sud-Ouest", description="Le mont Cameroun est situé dans le Sud-Ouest du Cameroun, à proximité de la côte atlantique, face à l'île de Bioko en Guinée équatoriale. Cette île, le mont Cameroun et d'autres volcans appartiennent à la ligne du Cameroun, un ensemble de volcans et de massifs volcaniques soulignant un rift allant du golfe de Guinée jusqu'au lac Tchad. Administrativement, le sommet de la montagne est situé à la limite des départements de Fako et de Meme, dans la région du Sud-Ouest. Douala, la plus grande ville du Cameroun, se trouve au sud-est. Il s'agit de l'un des plus grands volcans boucliers[2] ou stratovolcans[6],[8],[4] d'Afrique avec un volume de 1 400 km3[3],[8] et une superficie approchant les 1 300 km2[5]. Il a la forme d'une ellipse presque régulière, orientée sud-sud-ouest à nord-nord-est, d'environ 50 km par 35 à sa base. Ce volcan rouge est né du volcanisme du rift de la ligne du Cameroun[4] associé à celui d'un point chaud[7]. Il est composé de laves basaltiques à trachy-basaltiques[3],[8] telles des océanites, des hawaiites, des trachytes, des téphrites et des phonolites[2]. Le mont Cameroun forme une montagne isolée s'élevant au-dessus de plaines côtières[5]. Ces dernières sont composées de roches sédimentaires datant du Crétacé au Quaternaire et reposant sur des roches métamorphiques du Précambrien[3]. Les pentes régulières de la montagne sont interrompues par l'Etinde, au sud, ainsi qu'une profonde vallée partant du sommet et se dirigeant vers le nord-nord-ouest. Le volcan est couvert de son sommet au bas de ses pentes d'une centaine de bouches éruptives qui forment autant de cônes volcaniques. Ces bouches éruptives sont nées de fissures volcaniques ouvertes parallèlement à l'orientation de la montagne et au rift de la ligne du Cameroun. Le sommet du mont Cameroun est composé d'un plateau à environ 3 400 mètres d'altitude sur lequel se dressent des cônes et des cratères volcaniques. L'un d'eux, le Fako, constitue le point culminant de la montagne avec 4 040, 4 070, ou 4 095 mètres d'altitude. Cette altitude en fait le plus haut sommet d'Afrique occidentale et donc du Cameroun. La pluviométrie sur ses flancs est parmi les plus élevées d'Afrique[4] avec un record de 14 655 millimètres en 1919 à Debundscha[5]. Ces précipitations sont concentrées en été, durant les mois de juillet, août et septembre[5]. Toutefois, cette forte pluviométrie sur le bas des pentes de la montagne fait place à des conditions arides à partir de 3 000 mètres d'altitude en raison d'une inversion des températures qui bloque les nuages en dessous de cette altitude[4]. À ces altitudes élevées, les pluies laissent parfois place à de la neige[4]. ", tarif_adulte=3000, tarif_enfant=1500, image_url="mont_fako.jpeg"),
                    SiteTouristique(nom_site="Réserve du Dja", ville="Lomié", region="Est", description="La réserve de faune du Dja est une réserve faunique située au sud-est du Cameroun et établie comme réserve de biosphère en 1981. Créée en 1950, elle est inscrite au patrimoine mondial de l'UNESCO depuis 1987 grâce à la diversification des espèces présentes dans le parc et à la présence d'espèces en voie de disparition. La réserve est également reconnue en tant que réserve de biosphère par l'UNESCO depuis 1981 puis réserve de faune en 1982. La réserve est l'une des forêts humides d'Afrique les plus vastes (environ 5 000 km2) et les mieux protégées, la plus grande partie de sa superficie restant vierge, elle est parsemée de villages pygmées de l'ethnie Baka. Pratiquement encerclée par la rivière Dja, qui en forme la limite naturelle, la réserve est surtout remarquable pour sa biodiversité, puisqu'elle abrite 107 espèces de mammifères (dont quelques espèces menacées d'extinction) parmi lesquels l'éléphant de forêt d'Afrique, le perroquet gris du Gabon, le bongo, le léopard, et surtout pour la très grande variété des primates qui y vivent (le drill, le mandrill, le mangabey à collier blanc, le gorille des plaines de l’Ouest, le chimpanzé). Ensemble avec le parc national d'Odzala-Kokoua (République du Congo) et le parc national de Minkébé (Gabon), la réserve de faune du Dja fait partie de la zone TRIDOM (TRInationale du Dja, Odzala et Minkébé) du Fonds mondial pour la nature (WWF), qui est importante pour la protection des forêts denses africaines du bassin du Congo[5]. ", tarif_adulte=4000, tarif_enfant=2000, image_url="dja.jpg"),
                    SiteTouristique(nom_site="Palais de Foumban", ville="Foumban", region="Ouest", description="Le Palais des sultans bamouns est un édifice historique de la ville de Foumban, capitale du département Noun. Il est le siège du royaume Bamoun, où réside le sultan, roi du peuple bamoun établi à l'est de la rivière Noun. Le Palais royal de Foumban, où le roi des Bamouns réside encore de nos jours, a été construit en 1917 dans le style germanique bavarois. Le Musée du Palais raconte l'histoire de la dynastie des rois Bamoun de 1394 à nos jours, avec des informations sur le plus célèbre des rois bamoun, Ibrahim Njoya, décédé en 1933, qui créa à la fin du XIXe siècle un système d'écriture appelé l'écriture shü-mom. ", tarif_adulte=1500, tarif_enfant=750, image_url="foumban.jpg"),
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