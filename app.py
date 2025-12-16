
import sys
import os
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

from flask import Flask, request, render_template, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from models import * # db déclaré dans models.py
from crud_routes import crud  # importe les routes après db
from flask_migrate import Migrate   # ✅ AJOUT
import datetime
import uuid


# Ajouter le dossier du projet au chemin de recherche des modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer la base de données et les blueprints
from models import db, Client, Trajet, Reservation
from crud_routes import crud
from routes.locations import locations_bp
from routes.tourisme import tourisme_bp

# -------------------------
# INITIALISATION DE L'APP
# -------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://debora:ndenoka@localhost:5432/travelling'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'trefried1707'


# Initialiser SQLAlchemy
db.init_app(app)


db.init_app(app)   # lie db à app


# ✅ INITIALISATION FLASK-MIGRATE
migrate = Migrate(app, db)


# Enregistrer les blueprints
app.register_blueprint(crud)
app.register_blueprint(locations_bp)
app.register_blueprint(tourisme_bp)

# -------------------------
# ADMIN
# -------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            flash('Vous devez être connecté en tant qu\'administrateur', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

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

# -------------------------
# ROUTES PUBLIQUES/CLIENT
# -------------------------
@app.route("/")
def index():
    if session.get('admin'):
        return redirect(url_for('admin'))
    if session.get('client_id'):
        return redirect(url_for('public_dashboard'))
    return redirect(url_for('public_index'))

@app.route("/public")
@app.route("/public/index")
def public_index():
    return render_template("/public/index.html")


# Page de login client
@app.route("/public/login", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])


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
                password=generate_password_hash("default123"),  # Set a default password or manage it differently
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


@app.route("/public/login")
@app.route("/public/index/login")
@app.route("/login")

def public_login():
    if session.get('client_id'):
        return redirect(url_for('public_dashboard'))
    
    if request.method == "POST":
        telephone = request.form.get("telephone")
        client = Client.query.filter_by(telephone=telephone).first()
        if client:
            session['client_id'] = client.id_client
            flash('Connexion réussie ! Bienvenue', 'success')
            return redirect(url_for('public_dashboard'))
        else:
            flash('Client non trouvé. Veuillez vous inscrire.', 'error')
            return render_template("/public/login.html", error="Client non trouvé")
    
    return render_template("/public/login.html")


# Page d'inscription client
@app.route("/public/register", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])


@app.route("/public/login", methods=["POST"])
@app.route("/public/index/login", methods=["POST"])
@app.route("/login", methods=["POST"])
def handle_login():
    password = request.form.get("password")
    
    client = Client.query.filter_by(password=password).first()
    
    if client:
        session['client_id'] = client.id_client
        flash('Connexion réussie ! Bienvenue', 'success')
        return redirect(url_for('public_dashboard'))
    else:
        flash('Client non trouvé. Veuillez vous inscrire.', 'error')
        return render_template("/public/login.html", error="Client non trouvé")


@app.route("/public/register")
@app.route("/public/index/register")
@app.route("/register")

def public_register():
    if session.get('client_id'):
        return redirect(url_for('public_dashboard'))
    
    if request.method == "POST":
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        telephone = request.form.get("telephone")
        email = request.form.get("email")
        cni = request.form.get("cni")
        
        existing_client = Client.query.filter_by(telephone=telephone).first()
        if existing_client:
            flash('Ce numéro de téléphone est déjà enregistré', 'error')
            return render_template("/public/register.html", error="Ce numéro de téléphone est déjà enregistré")
        
        client = Client(nom=nom, prenom=prenom, telephone=telephone, email=email, cni=cni)
        db.session.add(client)
        db.session.commit()
        session['client_id'] = client.id_client
        flash('Inscription réussie ! Bienvenue chez MBOA TRAVEL', 'success')
        return redirect(url_for('public_dashboard'))
    
    return render_template("/public/register.html")


# Dashboard client


@app.route("/public/register", methods=["POST"])
@app.route("/public/index/register", methods=["POST"])
@app.route("/register", methods=["POST"])
def handle_register():
    nom = request.form.get("nom")
    prenom = request.form.get("prenom")
    telephone = request.form.get("telephone")
    email = request.form.get("email")
    cni = request.form.get("cni")
    password = request.form.get("password")
    
    # Vérifier si le client existe déjà
    existing_client = Client.query.filter_by(telephone=telephone).first()
    if existing_client:
        flash('Ce numéro de téléphone est déjà enregistré', 'error')
        return render_template("/public/register.html", error="Ce numéro de téléphone est déjà enregistré")
    
    # Créer le nouveau client
    client = Client(
        nom=nom,
        prenom=prenom,
        telephone=telephone,
        email=email,
        password=password,
        cni=cni
    )
    db.session.add(client)
    db.session.commit()
    
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

# Déconnexion client
@app.route("/logout")
@app.route("/public/logout")
def logout():
    session.pop('client_id', None)
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('public_index'))

@app.route("/public/contact")
def public_contact():
    return render_template("/public/contact.html")

# -------------------------
# TRAJETS PUBLICS
# -------------------------
@app.route("/public/trajets")
def public_trajets():
    trajets = Trajet.query.all()
    return render_template("/public/trajets.html", trajets=trajets)

@app.route("/trajets-publics")
def public_trajets_filtrees():
    depart = request.args.get('depart', '')
    arrivee = request.args.get('arrivee', '')

    query = Trajet.query
    if depart:
        query = query.filter(Trajet.ville_depart.ilike(f"%{depart}%"))
    if arrivee:
        query = query.filter(Trajet.ville_arrivee.ilike(f"%{arrivee}%"))

    trajets = query.all()
    return render_template("public/trajets.html", trajets=trajets)


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
    return render_template("public/liens_rapides.html")


# -------------------------
# PAGE RÉSERVATION (MANQUANTE — AJOUTÉE)
# -------------------------
@app.route("/public/reservation", methods=["GET", "POST"])
def public_reservation():
    if 'client_id' not in session:
        flash("Veuillez vous connecter pour réserver un billet", "error")
        return redirect(url_for('public_login'))

    trajets = Trajet.query.all()
    return render_template("public/reservation.html", trajets=trajets)

# -------------------------
# ERREURS
# -------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# -------------------------
# LANCEMENT DE L'APP
# -------------------------
if __name__ == "__main__":

    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")

    app.run(debug=True, host="0.0.0.0")

