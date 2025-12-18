from flask import Flask, request, render_template, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from models import *
from crud_routes import crud
from flask_migrate import Migrate
import datetime
import uuid
import os
from init_db import init_database

app = Flask(__name__)


# ============================================
# CONFIGURATION POUR DOCKER
# ============================================
# Utiliser DATABASE_URL si définie (Docker), sinon config locale
database_url = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:azerty@localhost/Travelling'
)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'trefried1707')

db.init_app(app)

# Initialisation Flask-Migrate
migrate = Migrate(app, db)

# Register blueprint
app.register_blueprint(crud)


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
    password = request.form.get("password") # Mot de passe en clair
    
    # ... Vérification si le client existe déjà ...
    # ...
    
    # Créer le nouveau client
    client = Client(
        nom=nom,
        prenom=prenom,
        telephone=telephone,
        email=email,
        # 🟢 CORRECTION : Hacher le mot de passe et l'assigner à password_hash
        password_hash=generate_password_hash(password),
        cni=cni
    )
    db.session.add(client)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Log l'erreur pour le debug (ex: violation d'une contrainte UNIQUE)
        print(f"Erreur lors de l l'inscription du client : {e}")
        flash("Une erreur est survenue (email ou CNI déjà utilisé ?)", 'error')
        return redirect(url_for('public_register'))


    # Connecter automatiquement le client
    session['client_id'] = client.id_client
    flash('Inscription réussie ! Bienvenue chez MBOA TRAVEL', 'success')
    return redirect(url_for('public_dashboard'))

@app.route("/public/contact")
@app.route("/public/index/contact")
@app.route("/contact", methods=["GET", "POST"])
def public_contact():
    if request.method == "POST":
        # traitement du formulaire ici
        flash("Message envoyé avec succès !", "success")
        return redirect(url_for("public_contact"))
    return render_template("/public/contact.html")



@app.route("/public/dashboard")
@app.route("/public/tableau_de_bord")
@app.route("/public/index/tableau_de_bord")
def public_dashboard():
    if 'client_id' not in session:
        flash('Veuillez vous connecter pour accéder à votre tableau de bord', 'error')
        return redirect(url_for('public_login'))
    
    client = Client.query.get(session['client_id'])
    
    if not client:
        session.pop('client_id', None)
        flash('Session expirée, veuillez vous reconnecter', 'error')
        return redirect(url_for('public_login'))
    
    return render_template("/public/dashboard.html", client=client)


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
    """Page des statistiques pour l'administrateur"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Statistiques générales
    total_clients = Client.query.count()
    total_voyages = Voyage.query.count()
    total_reservations = Reservation.query.count()
    total_agences = Agence.query.count()
    total_vehicules = Vehicule.query.count()
    total_personnels = Personnel.query.count()
    total_trajets = Trajet.query.count()
    
    # Revenus totaux
    revenus_totaux = db.session.query(func.sum(Paiement.montant)).scalar() or 0
    
    # Statistiques du mois en cours
    debut_mois = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    reservations_mois = Reservation.query.filter(Reservation.date_reservation >= debut_mois).count()
    
    revenus_mois = db.session.query(func.sum(Paiement.montant)).join(Reservation).filter(
        Reservation.date_reservation >= debut_mois
    ).scalar() or 0
    
    # Dernières réservations (5 dernières)
    dernieres_reservations = Reservation.query.order_by(
        Reservation.date_reservation.desc()
    ).limit(5).all()
    
    top_trajets = (
        db.session.query(
            Trajet.ville_depart,
            Trajet.ville_arrivee,
            func.count(Reservation.num_reservation).label('nb_reservations')
        )
        .select_from(Reservation)
        .join(Voyage, Reservation.id_voyage == Voyage.id_voyage)
        .join(Trajet, Voyage.id_trajet == Trajet.id_trajet)
        .group_by(
            Trajet.id_trajet,
            Trajet.ville_depart,
            Trajet.ville_arrivee
        )
        .order_by(func.count(Reservation.num_reservation).desc())
        .limit(5)
        .all()
    )

    
    # Répartition par mode de paiement
    paiements_par_mode = db.session.query(
        Paiement.mode,
        func.count(Paiement.id_paiement).label('nombre'),
        func.sum(Paiement.montant).label('montant_total')
    ).group_by(Paiement.mode).all()
    
    # Véhicules par statut
    vehicules_par_statut = db.session.query(
        Vehicule.statut,
        func.count(Vehicule.immatriculation).label('nombre')
    ).group_by(Vehicule.statut).all()
    
    # Réservations par jour (7 derniers jours)
    sept_jours = datetime.now() - timedelta(days=7)
    reservations_par_jour_raw = db.session.query(
        func.date(Reservation.date_reservation).label('date'),
        func.count(Reservation.num_reservation).label('nombre')
    ).filter(
        Reservation.date_reservation >= sept_jours
    ).group_by(
        func.date(Reservation.date_reservation)
    ).order_by(
        func.date(Reservation.date_reservation)
    ).all()

    reservations_par_jour = [
        {
            "date": r.date.strftime("%Y-%m-%d"),
            "nombre": r.nombre
        }
        for r in reservations_par_jour_raw
    ]
    ()
    
    # Taux d'occupation moyen
    voyages_avec_places = db.session.query(
        func.avg(Voyage.places_reservees).label('places_moyennes')
    ).scalar() or 0
    
    capacite_moyenne = db.session.query(
        func.avg(Vehicule.capacite)
    ).join(Voyage).scalar() or 1
    
    taux_occupation = (voyages_avec_places / capacite_moyenne * 100) if capacite_moyenne > 0 else 0
    
    return render_template(
        "admin/statistiques.html",
        total_clients=total_clients,
        total_voyages=total_voyages,
        total_reservations=total_reservations,
        total_agences=total_agences,
        total_vehicules=total_vehicules,
        total_personnels=total_personnels,
        total_trajets=total_trajets,
        revenus_totaux=revenus_totaux,
        reservations_mois=reservations_mois,
        revenus_mois=revenus_mois,
        dernieres_reservations=dernieres_reservations,
        top_trajets=top_trajets,
        paiements_par_mode=paiements_par_mode,
        vehicules_par_statut=vehicules_par_statut,
        reservations_par_jour=reservations_par_jour,
        taux_occupation=taux_occupation
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
    with app.app_context():
        # Cette ligne crée les tables si elles n'existent pas
        db.create_all()
        
        # Cette ligne vérifie si l'admin existe, sinon elle remplit la BD
        # (votre script init_database possède déjà les vérifications 'if not Admin.query.first()')
        try:
            init_database()
        except Exception as e:
            print(f"⚠️ Note: L'initialisation a déjà été faite ou a échoué : {e}")

    # Lancement de l'application
    app.run()