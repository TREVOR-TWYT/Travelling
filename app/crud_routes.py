from flask import Blueprint, request, jsonify,render_template,request, redirect, session, url_for,flash
from .models import db, Agence, Client, Trajet,Voyage,Reservation
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import random,string


crud = Blueprint("crud", __name__)

# ---------------------------------------------------
#                     ROUTES AGENCES
# ---------------------------------------------------

@crud.route("/agences", methods=["POST"])
def create_agence():
    data = request.json
    agence = Agence(
        nom_agence=data.get("nom_agence"),
        adresse=data.get("adresse")
    )
    db.session.add(agence)
    db.session.commit()

    return jsonify({"message": "Agence créée", "id": agence.id_agence}), 201

@crud.route("/agences", methods=["GET"])
def get_agences():
    agences = Agence.query.all()
    result = [
        {"id": a.id_agence, "nom": a.nom_agence, "adresse": a.adresse}
        for a in agences
    ]
    return jsonify(result)

@crud.route("/agences/<int:id>", methods=["GET"])
def get_agence(id):
    agence = Agence.query.get_or_404(id)
    return jsonify({
        "id": agence.id_agence,
        "nom": agence.nom_agence,
        "adresse": agence.adresse
    })

@crud.route("/agences/<int:id>", methods=["PUT"])
def update_agence(id):
    agence = Agence.query.get_or_404(id)
    data = request.json

    agence.nom_agence = data.get("nom_agence", agence.nom_agence)
    agence.adresse = data.get("adresse", agence.adresse)

    db.session.commit()
    return jsonify({"message": "Agence mise à jour"})

@crud.route("/agences/<int:id>", methods=["DELETE"])
def delete_agence(id):
    agence = Agence.query.get_or_404(id)
    db.session.delete(agence)
    db.session.commit()
    return jsonify({"message": "Agence supprimée"})


# ---------------------------------------------------
#                     ROUTES TRAJETS
# ---------------------------------------------------

@crud.route("/trajets", methods=["POST"])
def create_trajet():
    data = request.json

    trajet = Trajet(
        ville_depart=data["ville_depart"],
        ville_arrivee=data["ville_arrivee"],
        tarif_standard=data["tarif_standard"],
        tarif_vip=data["tarif_vip"]
    )

    db.session.add(trajet)
    db.session.commit()
    return jsonify({"message": "Trajet créé", "id": trajet.id_trajet}), 201

@crud.route("/trajets", methods=["GET"])
def get_trajets():
    trajets = Trajet.query.all()
    return jsonify([
        {
            "id": t.id_trajet,
            "depart": t.ville_depart,
            "arrivee": t.ville_arrivee,
            "tarif_standard": t.tarif_standard,
            "tarif_vip": t.tarif_vip
        }
        for t in trajets
    ])


# -----------------------------
# Décorateur pour protéger les routes
# -----------------------------
def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "client_id" not in session:
            flash("Veuillez vous inscrire ou vous connecter pour accéder à cette page.", "warning")
            return redirect(url_for("crud.register"))
        return f(*args, **kwargs)
    return wrapped

# -----------------------------
# REGISTER
# -----------------------------
@crud.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        telephone = request.form["telephone"]
        email = request.form["email"]
        password = request.form["password"]

        # Vérifier si le téléphone existe déjà
        existing_phone = Client.query.filter_by(telephone=telephone).first()
        if existing_phone:
            flash("Ce numéro de téléphone existe déjà.", "danger")
            return redirect(url_for("crud.register"))

        # Vérifier si l'email existe déjà
        if email:  # vérifier seulement si l'email n'est pas vide
            existing_email = Client.query.filter_by(email=email).first()
            if existing_email:
                flash("Cet email est déjà utilisé.", "danger")
                return redirect(url_for("crud.register"))

        # Hachage du mot de passe
        hashed_pw = generate_password_hash(password)

        # Création du nouveau client
        new_client = Client(
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            email=email,
            password=hashed_pw
        )

        db.session.add(new_client)
        db.session.commit()

        flash("Inscription réussie ! Connectez-vous.", "success")
        return redirect(url_for("crud.login"))

    return render_template("public/register.html")


# -----------------------------
# LOGIN
# -----------------------------
@crud.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        telephone = request.form["telephone"]
        password = request.form["password"]

        client = Client.query.filter_by(telephone=telephone).first()
        if not client or not check_password_hash(client.password, password):
            flash("Téléphone ou mot de passe incorrect.", "danger")
            return redirect(url_for("crud.login"))

        session["client_id"] = client.id_client
        session["client_nom"] = client.nom
        flash(f"Bienvenue {client.nom} !", "success")
        return redirect(url_for("crud.dashboard"))

    return render_template("public/login.html")

# -----------------------------
# DASHBOARD
# -----------------------------
@crud.route("/dashboard")
@login_required
def dashboard():
    client = Client.query.get(session["client_id"])
    return render_template("public/dashboard.html", client=client)

# -----------------------------
# PROFILE
# -----------------------------
@crud.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    client = Client.query.get(session["client_id"])

    if request.method == "POST":
        client.nom = request.form["nom"]
        client.prenom = request.form["prenom"]
        client.telephone = request.form["telephone"]
        client.email = request.form["email"]

        db.session.commit()
        flash("Profil mis à jour avec succès !", "success")
        return redirect(url_for("crud.profile"))

    return render_template("public/profile.html", client=client)

# -----------------------------
# LOGOUT et suppression du compte
# -----------------------------
@crud.route("/logout")
@login_required
def logout():
    client_id = session.get("client_id")
    if client_id:
        client = Client.query.get(client_id)
        if client:
            db.session.delete(client)  # Supprime le client de la base
            db.session.commit()
        session.clear()
        flash("Déconnexion réussie et votre compte a été supprimé.", "info")
    return redirect(url_for("index"))

# -----------------------------
# CONTACT
# -----------------------------
@crud.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        # Ici tu peux enregistrer en BD ou envoyer un mail
        flash("Votre message a été envoyé avec succès !", "success")
        return render_template("public/contact.html", success=True)

    return render_template("public/contact.html", success=False)

# -----------------------------
# AFFICHER LES TRAJETS
# -----------------------------
"""@crud.route("/trajets")
@login_required
def trajets():
    trajets = Trajet.query.all()
    return render_template("public/trajets.html", trajets=trajets)
"""

# -----------------------------
# RESERVATION DE VOYAGE
# -----------------------------
@crud.route("/reservation", methods=["GET"])
def reservation():
    ville_depart = request.args.get("ville_depart", "")
    ville_arrivee = request.args.get("ville_arrivee", "")

    if "client_id" not in session:
        flash("Veuillez vous connecter ou vous inscrire pour rechercher un trajet.", "warning")
        voyages = []  # aucun résultat affiché
        return render_template("public/reservation.html", voyages=voyages)

    # Si client connecté, effectuer la recherche
    voyages = Voyage.query.join("trajet")
    if ville_depart and ville_arrivee:
        voyages = voyages.filter(
            Voyage.trajet.has(ville_depart=ville_depart, ville_arrivee=ville_arrivee)
        )

    voyages = voyages.all()
    return render_template("public/reservation.html", voyages=voyages)


# -----------------------------
# RÉSERVER UN VOYAGE
# -----------------------------
@crud.route("/reserver/<int:id_voyage>", methods=["POST"])
@login_required
def reserver_voyage(id_voyage):
    client = Client.query.get(session["client_id"])
    voyage = Voyage.query.get_or_404(id_voyage)

    # Générer un numéro de réservation unique
    num_reservation = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    reservation = Reservation(
        num_reservation=num_reservation,
        date_reservation=datetime.now(),
        statut="En attente",
        id_client=client.id_client,
        id_voyage=voyage.id_voyage
    )

    db.session.add(reservation)
    db.session.commit()

    flash(f"Réservation effectuée ! Numéro : {num_reservation}", "success")
    return redirect(url_for("crud.dashboard"))
