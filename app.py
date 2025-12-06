from flask import Flask, request, render_template, redirect, session, url_for
from models import*
from crud_routes import crud

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://trevor:TREFRIED1707@localhost/travelling"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'trefried1707' 

db.init_app(app)

# Register blueprint
app.register_blueprint(crud)

#route pour la page d'acceuil
@app.route("/")
def index():
    return render_template("acceuil.html")

@app.route("/admin/layout")
def admin():
    return render_template("/admin/layout.html")

@app.route("/public/index")
def public_index():
    return render_template("/public/index.html")

@app.route("/public/index/reservation")
def public_reservation():
    return render_template("/public/reservation.html")

@app.route("/public/index/login", methods=["GET", "POST"])
def public_login():
    if request.method == "POST":
        telephone = request.form.get("telephone")
        # Vous pouvez ajouter un système de mot de passe plus tard
        
        from models import Client
        client = Client.query.filter_by(telephone=telephone).first()
        
        if client:
            session['client_id'] = client.id_client
            return redirect(url_for('public_dashboard'))
        else:
            return render_template("/public/login.html", error="Client non trouvé")
    
    return render_template("/public/login.html")

@app.route("/logout")
def logout():
    session.pop('client_id', None)
    return redirect(url_for('index'))

@app.route("/login", methods=["GET", "POST"])
def login():
    return public_login()

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        telephone = request.form.get("telephone")
        email = request.form.get("email")
        cni = request.form.get("cni")
        
        # Vérifier si le client existe déjà
        existing_client = Client.query.filter_by(telephone=telephone).first()
        if existing_client:
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
        return redirect(url_for('public_dashboard'))
    
    return render_template("/public/register.html")

@app.route("/recherche")
def recherche():
    if 'client_id' not in session:
        return redirect(url_for('public_login'))
    return redirect(url_for('crud.reservation'))


@app.route("/mes-reservations")
def mes_reservations():
    if 'client_id' not in session:
        return redirect(url_for('public_login'))
    
    from models import Client, Reservation
    client = Client.query.get(session['client_id'])
    reservations = Reservation.query.filter_by(id_client=client.id_client).all()
    
    return render_template("/public/mes_reservations.html", 
                         client=client, 
                         reservations=reservations)

@app.route("/contact")
def contact_dashboard():
    return redirect(url_for('public_contact'))   

@app.route("/public/index/contact")
def public_contact():
    return render_template("/public/contact.html")

@app.route("/public/index/tableau_de_bord")
def public_dashboard():
    # Vérifier si l'utilisateur est connecté
    if 'client_id' not in session:
        return redirect(url_for('public_login'))
    
    # Récupérer les informations du client
    from models import Client
    client = Client.query.get(session['client_id'])
    
    if not client:
        return redirect(url_for('public_login'))
    
    return render_template("/public/dashboard.html", client=client)

@app.route("/public/index/trajets")
def trajets_list():
    trajets = Trajet.query.all()
    return render_template("/trajets/list.html", trajets=trajets)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")
