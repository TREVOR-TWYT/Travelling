import sys
import os
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

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
    if session.get('admin'):
        return redirect(url_for('admin'))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session["admin"] = True
            session.permanent = True
            flash('Connexion réussie !', 'success')
            return redirect(url_for('admin'))
        
        flash('Identifiants incorrects', 'error')
        return render_template("admin/login_admin.html", error="Identifiants incorrects")
    
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

