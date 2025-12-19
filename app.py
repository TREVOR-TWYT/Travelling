from flask import Flask, request, render_template, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from models import *
from crud_routes import crud
from tourism_routes import tourism
from flask_migrate import Migrate
from datetime import datetime, timedelta
import uuid
import os
import random
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
#from init_db import init_database


app = Flask(__name__)


# ============================================
# CONFIGURATION POUR DOCKER
# ============================================
# Utiliser DATABASE_URL si définie (Docker), sinon config locale
database_url = os.environ.get(
    'DATABASE_URL',
    #"postgresql://alex:Bf1im16y@localhost/travelling"
    "postgresql://trevor:TREFRIED1707@localhost/travelling"
)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'trefried1707')
# Configuration de Flask-Mail (Exemple Gmail)
app.config['MAIL_DEFAULT_SENDER'] = 'mboatravel@gmail.com'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mboatravel@gmail.com'
app.config['MAIL_PASSWORD'] = 'epmz jjzq ujea odmy' # Le code de 16 caractères

mail = Mail(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

db.init_app(app)

# Initialisation Flask-Migrate
migrate = Migrate(app, db)

# Register blueprint
app.register_blueprint(crud)
app.register_blueprint(tourism)




# ============================================
# INITIALISATION AUTOMATIQUE (SOLIDE)
# ============================================
with app.app_context():
    db.create_all()
    try:
        # On passe directement les objets app et db ici
        init_database() 
    except Exception as e:
        print(f"⚠️ Note: {e}")




# ============================================
# DÉCORATEUR POUR PROTÉGER LES ROUTES ADMIN
# ============================================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            flash('Vous devez être connecté en tant qu\'administrateur', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# ROUTE RACINE - REDIRECTION INTELLIGENTE
# ============================================
@app.route("/")
def index():
    # Si admin connecté, aller vers admin
    if session.get('admin'):
        return redirect(url_for('admin'))
    
    # Si client connecté, aller vers dashboard client
    if session.get('client_id'):
        return redirect(url_for('public_dashboard'))
    
    # Sinon, rediriger vers la page publique
    return redirect(url_for('public_index'))


# ============================================
# ROUTES ADMIN
# ============================================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    # Si l’admin est déjà connecté
    if session.get('admin'):
        return redirect(url_for('admin'))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Recherche dans la base
        admin = Admin.query.filter_by(nom=username).first()

        # Vérification utilisateur + mot de passe
        if admin and check_password_hash(admin.password_hash, password):
            session["admin"] = admin.id     # On stocke l'ID en session
            session.permanent = True
            flash('Connexion réussie !', 'success')
            return redirect(url_for('admin'))

        # Sinon : erreur
        flash('Identifiants incorrects', 'error')
        return render_template("admin/login_admin.html", error="Identifiants incorrects")

    # Méthode GET → afficher page login
    return render_template("admin/login_admin.html")


@app.route("/admin-logout")
def admin_logout():
    session.pop('admin', None)
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('admin_login'))


@app.route("/admin/layout")
@app.route("/admin")
@admin_required
def admin():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    return render_template("/admin/layout.html")


# ============================================
# ROUTES PUBLIQUES/CLIENT
# ============================================
@app.route("/public")
@app.route("/public/index")
def public_index():
    return render_template("/public/index.html")


@app.route("/public/reservation", methods=["GET"])
@app.route("/public/index/reservation", methods=["GET"])
def public_reservation():
    """Page de réservation publique avec recherche de voyages"""
    # Récupérer les paramètres de recherche
    ville_depart = request.args.get('ville_depart', '')
    ville_arrivee = request.args.get('ville_arrivee', '')
    date_depart = request.args.get('date_depart', '')
    
    # Si des critères de recherche sont fournis, filtrer les voyages
    if ville_depart or ville_arrivee or date_depart:
        query = Voyage.query.join(Trajet)
        
        if ville_depart:
            query = query.filter(Trajet.ville_depart.ilike(f"%{ville_depart}%"))
        
        if ville_arrivee:
            query = query.filter(Trajet.ville_arrivee.ilike(f"%{ville_arrivee}%"))
        
        if date_depart:
            query = query.filter(Voyage.date_depart == date_depart)
        
        voyages = query.all()
    else:
        # Afficher tous les voyages disponibles
        voyages = Voyage.query.all()
    
    return render_template("/public/reservation.html", voyages=voyages)

@app.route('/reservation/confirmation', methods=['POST'])
def reservation_confirmation():
    try:
        id_voyage = request.form.get("id_voyage")
        montant = int(request.form.get("montant"))
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        telephone = request.form.get("telephone")
        email = request.form.get("email")
        mode_paiement = request.form.get("mode")

        # 1️⃣ Vérifier le voyage
        voyage = db.session.get(Voyage, id_voyage)
        if not voyage:
            flash("Voyage introuvable.", "error")
            return redirect(url_for('public_reservation'))

        # 2️⃣ Vérifier si le client existe déjà (par téléphone)
        client = Client.query.filter_by(telephone=telephone).first()
        if not client:
            client = Client(
                nom=nom,
                prenom=prenom,
                telephone=telephone,
                email=email,
                password_hash=generate_password_hash("default123"),  # Set a default password or manage it differently
                cni="none"
            )
            db.session.add(client)
            db.session.commit()

        # 3️⃣ Création d'un paiement
        paiement = Paiement(
            montant=montant,
            date_paiement=datetime.datetime.utcnow(),
            mode=mode_paiement,
            reference_transaction=f"REF-{uuid.uuid4().hex[:10].upper()}"
        )
        db.session.add(paiement)
        db.session.commit()
            # 4️⃣ Incrémenter les places réservées pour le voyage
        voyage.places_reservees += 1
        db.session.commit()

        # 5️⃣ Créer la réservation
        reservation = Reservation(
            num_reservation=f"RSV-{uuid.uuid4().hex[:8].upper()}",
            date_reservation=datetime.datetime.utcnow(),
            statut="Confirmée",
            id_client=client.id_client,
            id_voyage=id_voyage,
            id_paiement=paiement.id_paiement
        )
        db.session.add(reservation)
        db.session.commit()

        flash("🎉 Réservation effectuée avec succès !", "success")

        # On affiche une page de confirmation
        return render_template(
            "/public/confirmation.html",
            voyage=voyage,
            client=client,
            montant=montant,
            mode=mode_paiement,
            reservation=reservation
        )

    except Exception as e:
        print(e)
        flash("Une erreur s'est produite lors de la réservation.", "error")
        return redirect(url_for('public_reservation'))


# ============================================
# ROUTES PUBLIQUES/CLIENT (Connexion)
# ============================================

# 1. Fonction pour AFFICHER le formulaire de connexion (Méthode GET)
# Endpoint utilisé dans url_for : 'public_login'
@app.route("/public/login", endpoint='public_login', methods=["GET"])
@app.route("/public/index/login", endpoint='public_login', methods=["GET"])
@app.route("/login", endpoint='public_login', methods=["GET"])
def public_login():
    """Affiche la page de connexion client."""
    if session.get('client_id'):
        return redirect(url_for('public_dashboard'))
    return render_template("/public/login.html")


# 2. Fonction pour TRAITER la soumission du formulaire (Méthode POST)
# Endpoint utilisé par le formulaire : 'handle_client_login' (ou l'URL /login)
@app.route("/public/login", endpoint='handle_client_login', methods=["POST"])
@app.route("/public/index/login", endpoint='handle_client_login', methods=["POST"])
@app.route("/login", endpoint='handle_client_login', methods=["POST"])
def handle_client_login():
    """Traite la soumission du formulaire de connexion client."""
    identifier = request.form.get("identifier") 
    password = request.form.get("password")
    
    # Vérifier l'existence d'un identifiant
    if not identifier or not password:
        flash('Veuillez entrer l\'identifiant et le mot de passe.', 'error')
        # Redirection vers l'endpoint GET
        return redirect(url_for('public_login'))

    # Tentative de recherche par Email
    client = Client.query.filter_by(email=identifier).first()
    
    # Si le client n'est pas trouvé par email, essayer par téléphone
    if not client:
        client = Client.query.filter_by(telephone=identifier).first()
    
    # Vérification: Client trouvé ET mot de passe correct
    if client and client.check_password(password):
        session['client_id'] = client.id_client
        flash('Connexion réussie ! Bienvenue', 'success')
        return redirect(url_for('public_dashboard'))
    else:
        # Échec : Client non trouvé OU mot de passe incorrect
        flash('Identifiants ou mot de passe incorrects.', 'error')
        # Retourne sur la page de login avec le message d'erreur
        return render_template("/public/login.html", error="Identifiants incorrects")

# ============================================
# ROUTES PUBLIQUES/CLIENT (Inscription)
# ============================================

# 1. Fonction pour AFFICHER le formulaire d'inscription (Méthode GET)
# ⭐ CORRECTION: Ajout explicite de l'endpoint 'public_register' pour Jinja
@app.route("/public/register", endpoint='public_register', methods=["GET"])
@app.route("/public/index/register", endpoint='public_register', methods=["GET"])
@app.route("/register", endpoint='public_register', methods=["GET"])
def public_register():
    if session.get('client_id'):
        return redirect(url_for('public_dashboard'))
    return render_template("/public/register.html")


# 2. Fonction pour TRAITER l'inscription (Méthode POST)
# ⭐ CORRECTION: Ajout explicite de l'endpoint 'handle_register' pour Flask
@app.route("/public/register", endpoint='handle_register', methods=["POST"])
@app.route("/public/index/register", endpoint='handle_register', methods=["POST"])
@app.route("/register", endpoint='handle_register', methods=["POST"])
def handle_register():
    nom = request.form.get("nom")
    prenom = request.form.get("prenom")
    telephone = request.form.get("telephone")
    email = request.form.get("email")
    cni = request.form.get("cni")
    password = request.form.get("password")

    # 1. Vérification si le client existe déjà
    existing_client = Client.query.filter((Client.email == email) | (Client.telephone == telephone)).first()
    if existing_client:
        flash("Un compte avec cet email ou ce numéro existe déjà.", "error")
        return redirect(url_for('public_register'))

    # 2. Génération du code à 6 chiffres
    otp_code = str(random.randint(100000, 999999))

    # 3. Stockage des infos en SESSION (temporaire)
    # On hache le mot de passe ici pour la sécurité
    session['temp_user'] = {
        "nom": nom,
        "prenom": prenom,
        "telephone": telephone,
        "email": email,
        "cni": cni,
        "password_hash": generate_password_hash(password),
        "otp": otp_code
    }

    # 4. Envoi de l'email avec le CODE
    try:
        msg = Message('Votre code de vérification - MBOA TRAVEL', recipients=[email])
        msg.body = f"Bonjour {nom},\n\nVotre code de confirmation est : {otp_code}\n\nEntrez ce code sur la page de vérification pour activer votre compte."
        mail.send(msg)
        
        flash('Un code de vérification a été envoyé par email.', 'info')
        return redirect(url_for('verify_email')) # On redirige vers la page de saisie du code
        
    except Exception as e:
        print(f"Erreur mail : {e}")
        flash("Erreur lors de l'envoi du code. Vérifiez votre adresse.", 'error')
        return redirect(url_for('public_register'))

#C'est ici qu'on compare le code tapé avec celui stocké en session. Si c'est bon, on enregistre enfin dans la base de données.
@app.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    if 'temp_user' not in session:
        flash("Session expirée. Veuillez vous réinscrire.", "error")
        return redirect(url_for('public_register'))

    if request.method == "POST":
        # ACTION 1 : RENVOYER LE CODE
        if 'action_resend' in request.form:
            new_otp = str(random.randint(100000, 999999))
            user_data = session['temp_user']
            user_data['otp'] = new_otp
            session['temp_user'] = user_data # Mise à jour session
            
            try:
                msg = Message('Nouveau code - MBOA TRAVEL', recipients=[user_data['email']])
                msg.body = f"Votre nouveau code est : {new_otp}"
                mail.send(msg)
                flash("Un nouveau code a été envoyé !", "info")
            except:
                flash("Erreur d'envoi.", "error")
            return render_template("public/verification_otp.html")

        # ACTION 2 : VÉRIFIER LE CODE (Action par défaut)
        code_entre = request.form.get("otp")
        user_data = session['temp_user']

        if code_entre == user_data['otp']:
            # Création du client en base de données
            new_client = Client(
                nom=user_data['nom'],
                prenom=user_data['prenom'],
                telephone=user_data['telephone'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                cni=user_data['cni']
            )
            db.session.add(new_client)
            db.session.commit()

            client_id = new_client.id_client
            session.pop('temp_user', None)
            session['client_id'] = client_id
            flash('Inscription réussie !', 'success')
            return redirect(url_for('public_dashboard'))
        else:
            flash("Code incorrect.", "error")

    return render_template("public/verification_otp.html")


@app.route("/public/contact")
@app.route("/public/index/contact")
@app.route("/contact", methods=["GET", "POST"])
def public_contact():
    if request.method == "POST":
        nom_complet = request.form.get("name")
        email_client = request.form.get("email")
        message_contenu = request.form.get("message")

        # --- 1. EMAIL POUR VOUS (Notification) ---
        msg_admin = Message(
            subject=f"Nouveau message de {nom_complet}",
            recipients=[app.config['MAIL_USERNAME']],
            sender=app.config['MAIL_DEFAULT_SENDER'],
            reply_to=email_client
        )
        # ✅ CORRECTION : Utilisation du bon nom d'objet et de variable
        msg_admin.body = f"""
Nouveau message reçu depuis MBOA TRAVEL :
------------------------------------------
Nom : {nom_complet}
Email : {email_client}

Message :
{message_contenu}
------------------------------------------
"""

        # --- 2. EMAIL POUR LE CLIENT (Accusé de réception) ---
        msg_client = Message(
            subject="Nous avons bien reçu votre message - MBOA TRAVEL",
            recipients=[email_client],
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        msg_client.body = f"""
Bonjour {nom_complet},

Merci d'avoir contacté MBOA TRAVEL ! 

Nous avons bien reçu votre message. Notre équipe examine votre requête et vous répondra sous 24h.

Détails de votre message :
------------------------------------------
"{message_contenu}"
------------------------------------------

Cordialement,
L'équipe MBOA TRAVEL
"""

        try:
            # Envoi synchronisé
            mail.send(msg_admin)
            mail.send(msg_client)
            flash("Message envoyé avec succès ! Un accusé de réception vous a été envoyé.", "success")
        except Exception as e:
            print(f"Erreur d'envoi : {e}")
            flash("Erreur lors de l'envoi du message.", "error")
        
        return redirect(url_for("public_contact"))

    return render_template("public/contact.html")


@app.route("/public/dashboard")
@app.route("/public/tableau_de_bord")
@app.route("/public/index/tableau_de_bord")
def public_dashboard():
    from sqlalchemy import desc
    
    if 'client_id' not in session:
        flash('Veuillez vous connecter pour accéder à votre tableau de bord', 'error')
        return redirect(url_for('public_login'))
    
    client_id = session['client_id']
    # Utilisation de db.session.get pour éviter l'avertissement Legacy
    client = db.session.get(Client, client_id)
    
    if not client:
        session.pop('client_id', None)
        return redirect(url_for('public_login'))

    # --- RÉCUPÉRATION DES DONNÉES (Noms basés sur ton models.py) ---
    
    stats = {
        'bus': Reservation.query.filter_by(id_client=client_id).count(),
        'excursions': ReservationExcursion.query.filter_by(id_client=client_id).count(),
        'locations': LocationVehicule.query.filter_by(id_client=client_id).count(),
        'colis': Expedition.query.filter_by(id_client_expediteur=client_id).count() # Corrigé ici
    }

    # Dernier Ticket de Bus
    # Trié par date_reservation (le plus récent en premier)
    dernier_ticket = Reservation.query.filter_by(id_client=client_id)\
        .order_by(desc(Reservation.date_reservation)).first()

    # Dernier Colis
    # Trié par date_expedition (le plus récent en premier)
    dernier_colis = Expedition.query.filter_by(id_client_expediteur=client_id)\
        .order_by(desc(Expedition.date_expedition)).first()

    return render_template(
        "/public/dashboard.html", 
        client=client, 
        stats=stats,
        dernier_ticket=dernier_ticket,
        dernier_colis=dernier_colis
    )

# -----------------------------
# PROFILE
# -----------------------------
@app.route("/public/profile", methods=["GET", "POST"])
#@login_required
def public_profile():
    client = db.session.get(Client, session["client_id"])

    if request.method == "POST":
        client.nom = request.form["nom"]
        client.prenom = request.form["prenom"]
        client.telephone = request.form["telephone"]
        client.email = request.form["email"]

        db.session.commit()
        flash("Profil mis à jour avec succès !", "success")
        return redirect(url_for("public_profile"))

    return render_template("public/profile.html", client=client)


@app.route("/public/trajets")
@app.route("/trajets-publics")
def public_trajets():
    """Route publique pour afficher les trajets aux clients"""
    # Récupérer les filtres optionnels
    depart = request.args.get('depart', '')
    arrivee = request.args.get('arrivee', '')
    
    # Construire la requête
    query = Trajet.query
    
    if depart:
        query = query.filter(Trajet.ville_depart.ilike(f"%{depart}%"))
    
    if arrivee:
        query = query.filter(Trajet.ville_arrivee.ilike(f"%{arrivee}%"))
    
    trajets = query.all()
    
    return render_template("public/trajets.html", trajets=trajets)

@app.route("/logout")
@app.route("/public/logout")
def logout():
    session.pop('client_id', None)
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('public_index'))


@app.route("/recherche")
def recherche():
    if 'client_id' not in session:
        flash('Veuillez vous connecter pour effectuer une recherche', 'error')
        return redirect(url_for('public_login'))
    return redirect(url_for('crud.reservation'))


@app.route("/mes-reservations")
def mes_reservations():
    if 'client_id' not in session:
        flash('Veuillez vous connecter pour voir vos réservations', 'error')
        return redirect(url_for('public_login'))
    
    client = Client.query.get(session['client_id'])
    if not client:
        session.pop('client_id', None)
        return redirect(url_for('public_login'))
    
    reservations = Reservation.query.filter_by(id_client=client.id_client).all()
    
    return render_template("/public/mes_reservations.html", 
                         client=client, 
                         reservations=reservations)


@app.route("/admin/statistiques")
@admin_required
def admin_statistiques():
    from sqlalchemy import func, desc
    
    
    # --- 1. COMPTAGES DE BASE (Sûr) ---
    total_clients = Client.query.count()
    total_agences = Agence.query.count()
    total_vehicules = Vehicule.query.count()
    total_personnels = Personnel.query.count()

    # --- 2. CALCUL DES REVENUS (Sécurisé par try/except) ---
    def get_revenue(model_class):
        try:
            # On tente de joindre via la relation automatique de SQLAlchemy
            return db.session.query(func.sum(Paiement.montant)).join(model_class).scalar() or 0
        except Exception:
            db.session.rollback()
            return 0

    revenus_transport = get_revenue(Reservation)
    revenus_tourisme = get_revenue(ReservationExcursion)
    revenus_locations = get_revenue(LocationVehicule)
    revenus_expeditions = get_revenue(Expedition)
    
    revenus_totaux = revenus_transport + revenus_tourisme + revenus_locations + revenus_expeditions

    # --- 3. LOGISTIQUE ET VOLUMES ---
    total_excursions = Excursion.query.count()
    total_reservations = Reservation.query.count()
    total_expeditions = Expedition.query.count()
    
    # Gestion du statut colis (vérifie si 'statut' existe)
    try:
        colis_en_transit = StatutColis.query.filter(StatutColis.statut.in_(['En cours', 'Expédié', 'Enregistré'])).count()
        print(f"DEBUG: Colis trouvés = {colis_en_transit}")
    except Exception as e:
        print(f"ERREUR SQLALCHEMY : {e}")
        colis_en_transit = 0


    # Top Sites (Requête simplifiée pour éviter les erreurs de jointures complexes)
    try:
        top_sites = db.session.query(
            SiteTouristique.nom_site,
            func.count(ReservationExcursion.id).label('nb_reservations')
        ).join(Excursion).join(ReservationExcursion)\
         .group_by(SiteTouristique.nom_site).order_by(desc('nb_reservations')).limit(5).all()
    except:
        top_sites = []

    # Flotte
    loc_disponibles = Vehicule.query.filter_by(statut='En service').count()
    loc_loues = Vehicule.query.filter_by(statut='Loué').count()
    loc_maintenance = Vehicule.query.filter_by(statut='Maintenance').count()

    # --- 4. DERNIÈRES ACTIVITÉS (Version Auto-Détectrice) ---
    from sqlalchemy import inspect

    def get_recent(model_class, limit=3):
        try:
            # Cette ligne trouve automatiquement le nom de la clé primaire (id, num_res, etc.)
            pk_name = inspect(model_class).primary_key[0].name
            return model_class.query.order_by(desc(getattr(model_class, pk_name))).limit(limit).all()
        except Exception as e:
            print(f"Erreur lors de la récupération de {model_class}: {e}")
            return []

    res_recentes = get_recent(Reservation)
    exc_recentes = get_recent(ReservationExcursion)
    loc_recentes = get_recent(LocationVehicule)
    exp_recentes = get_recent(Expedition)

    dernières_activites = []
    
    # 1. Ajout Transport
    for r in res_recentes:
        dernières_activites.append({
            'date': getattr(r, 'date_reservation', datetime.now()),
            'service_type': '🚌 Transport',
            'nom_client': r.client.nom if (hasattr(r, 'client') and r.client) else "Client",
            'info_objet': f"Voyage #{getattr(r, inspect(Reservation).primary_key[0].name, '')}",
            'montant': r.paiement.montant if (hasattr(r, 'paiement') and r.paiement) else 0,
            'statut': getattr(r, 'statut', 'Confirmé')
        })

    # 2. Ajout Tourisme
    for e in exc_recentes:
        dernières_activites.append({
            'date': getattr(e, 'date_reservation', datetime.now()),
            'service_type': '🏖️ Tourisme',
            'nom_client': e.client.nom if (hasattr(e, 'client') and e.client) else "Client",
            'info_objet': e.excursion.nom_excursion if hasattr(e, 'excursion') else "Excursion",
            'montant': e.paiement.montant if (hasattr(e, 'paiement') and e.paiement) else 0,
            'statut': 'Confirmé'
        })

    # 3. Ajout Expéditions
    for ex in exp_recentes:
        dernières_activites.append({
            'date': getattr(ex, 'date_expedition', datetime.now()),
            'service_type': '📦 Expédition',
            'nom_client': ex.client.nom if (hasattr(ex, 'client') and ex.client) else "Expéditeur",
            'info_objet': f"Colis vers {getattr(ex, 'ville_destination', 'Destination')}",
            'montant': ex.paiement.montant if (hasattr(ex, 'paiement') and ex.paiement) else 0,
            'statut': getattr(ex, 'statut', 'Envoi')
        })

    # Tri final par date
    dernières_activites = sorted(dernières_activites, key=lambda x: x['date'], reverse=True)[:10]

    # --- 5. GRAPHES ---
    aujourdhui = datetime.now()
    sept_jours_vrai = [ (aujourdhui - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1) ]
    
    reservations_par_jour = []
    try:
        # On récupère les données
        res_par_jour = db.session.query(
            func.date(Reservation.date_reservation).label('date'),
            func.count(Reservation.id).label('nombre')
        ).filter(Reservation.date_reservation >= (aujourdhui - timedelta(days=7)))\
         .group_by(func.date(Reservation.date_reservation)).all()
        
        # On transforme en dictionnaire pour un accès facile : {"2025-12-19": 5}
        stats_dict = {r.date.strftime("%Y-%m-%d"): r.nombre for r in res_par_jour}
        
        # On remplit pour CHAQUE jour (même si c'est 0) pour que le graphique soit beau
        for d in sept_jours_vrai:
            reservations_par_jour.append({
                "date": d,
                "nombre": stats_dict.get(d, 0) # Met 0 si aucune réservation ce jour-là
            })
    except Exception as e:
        print(f"Erreur graphique : {e}")
        # En cas d'erreur, on envoie des données bidon à 0 pour ne pas casser le JS
        reservations_par_jour = [{"date": d, "nombre": 0} for d in sept_jours_vrai]

    return render_template(
        "admin/statistiques.html",
        total_clients=total_clients, total_agences=total_agences,
        total_vehicules=total_vehicules, total_personnels=total_personnels,
        revenus_totaux=revenus_totaux, revenus_transport=revenus_transport,
        revenus_tourisme=revenus_tourisme, revenus_locations=revenus_locations,
        revenus_expeditions=revenus_expeditions, total_excursions=total_excursions,
        total_reservations=total_reservations, top_sites=top_sites,
        loc_disponibles=loc_disponibles, loc_loues=loc_loues,
        loc_maintenance=loc_maintenance, colis_en_transit=colis_en_transit,
        dernières_activites=dernières_activites, reservations_par_jour=reservations_par_jour
    )

# ============================================
# PAGE LIENS RAPIDES (POUR DÉVELOPPEMENT)
# ============================================
@app.route("/liens-rapides")
def liens_rapides():
    """Page avec tous les liens utiles pour le développement"""
    return render_template("public/liens_rapides.html")


# ============================================
# GESTION DES ERREURS
# ============================================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
