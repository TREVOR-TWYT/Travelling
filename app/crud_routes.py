from flask import Blueprint, request, jsonify,render_template,request, redirect, session, url_for
from .models import db, Agence, Client, Trajet,Voyage

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
#                     ROUTES CLIENTS
# ---------------------------------------------------

@crud.route("/clients", methods=["POST"])
def create_client():
    data = request.json

    client = Client(
        nom=data.get("nom"),
        prenom=data.get("prenom"),
        telephone=data.get("telephone"),
        email=data.get("email"),
        cni=data.get("cni")
    )
    db.session.add(client)
    db.session.commit()

    return jsonify({"message": "Client créé", "id": client.id_client}), 201

@crud.route("/clients", methods=["GET"])
def get_clients():
    clients = Client.query.all()
    return jsonify([
        {
            "id": c.id_client,
            "nom": c.nom,
            "prenom": c.prenom,
            "telephone": c.telephone,
            "email": c.email,
            "cni": c.cni
        }
        for c in clients
    ])

@crud.route("/clients/<int:id>", methods=["PUT"])
def update_client(id):
    client = Client.query.get_or_404(id)
    data = request.json

    for field in ["nom", "prenom", "telephone", "email", "cni"]:
        setattr(client, field, data.get(field, getattr(client, field)))

    db.session.commit()
    return jsonify({"message": "Client mis à jour"})

@crud.route("/clients/<int:id>", methods=["DELETE"])
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Client supprimé"})


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


@crud.route('/reservation', methods=['GET'])
def reservation():
    ville_depart = request.args.get('ville_depart', '')
    ville_arrivee = request.args.get('ville_arrivee', '')
    
    voyages = Voyage.query.join('trajet')
    
    if ville_depart and ville_arrivee:
        voyages = voyages.filter(
            Voyage.trajet.has(ville_depart=ville_depart, ville_arrivee=ville_arrivee)
        )
    
    voyages = voyages.all()
    
    return render_template('reservation.html', voyages=voyages)


@crud.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        # plus tard tu pourras enregistrer en BD ou envoyer un mail

        return render_template("contact.html", success=True)

    return render_template("contact.html", success=False)


@crud.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        telephone = request.form.get("telephone")

        # Vérifier si le numéro existe déjà
        client_exist = Client.query.filter_by(telephone=telephone).first()
        if client_exist:
            error = "Ce numéro est déjà enregistré."
            return render_template("register.html", error=error)

        # Créer un nouveau client
        new_client = Client(
            nom=nom,
            prenom=prenom,
            telephone=telephone
        )

        db.session.add(new_client)
        db.session.commit()

        # Stocker la session
        session["client_id"] = new_client.id_client

        return redirect("/dashboard")

    return render_template("register.html")

@crud.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        telephone = request.form.get("telephone")

        client = Client.query.filter_by(telephone=telephone).first()

        if not client:
            error = "Numéro introuvable. Veuillez vous inscrire."
            return render_template("login.html", error=error)

        # Connexion OK
        session["client_id"] = client.id_client
        return redirect("/dashboard")

    return render_template("login.html")

@crud.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@crud.route("/dashboard")
def dashboard():
    if "client_id" not in session:
        return redirect("/login")

    client = Client.query.get(session["client_id"])

    return render_template("dashboard.html", client=client)
