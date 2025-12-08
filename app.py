from flask import Flask, request, render_template, redirect, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from models import *
from crud_routes import crud

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://trevor:TREFRIED1707@localhost/travelling"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'trefried1707'

db.init_app(app)

# Register blueprint
app.register_blueprint(crud)

# ============================================
# CONFIGURATION ADMIN
# ============================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin")


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


# ============================================
# ROUTES PUBLIQUES/CLIENT
# ============================================
@app.route("/public")
@app.route("/public/index")
def public_index():
    return render_template("/public/index.html")


@app.route("/public/reservation")
@app.route("/public/index/reservation")
def public_reservation():
    return render_template("/public/reservation.html")


@app.route("/public/login")
@app.route("/public/index/login")
@app.route("/login")
def public_login():
    if session.get('client_id'):
        return redirect(url_for('public_dashboard'))
    return render_template("/public/login.html")


@app.route("/public/login", methods=["POST"])
@app.route("/public/index/login", methods=["POST"])
@app.route("/login", methods=["POST"])
def handle_login():
    telephone = request.form.get("telephone")
    
    client = Client.query.filter_by(telephone=telephone).first()
    
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
    return render_template("/public/register.html")


@app.route("/public/register", methods=["POST"])
@app.route("/public/index/register", methods=["POST"])
@app.route("/register", methods=["POST"])
def handle_register():
    nom = request.form.get("nom")
    prenom = request.form.get("prenom")
    telephone = request.form.get("telephone")
    email = request.form.get("email")
    cni = request.form.get("cni")
    
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
@app.route("/contact")
def public_contact():
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
        db.create_all()
    app.run(debug=True, host="0.0.0.0")