from flask import Blueprint, request, render_template, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash
from models import*
import datetime
import uuid

crud = Blueprint("crud", __name__)

# LISTE DES AGENCES
@crud.route("/agences")
def list_agences():
    agences = Agence.query.all()
    return render_template("admin/agences/list.html", agences=agences)

# CREER UNE AGENCE
@crud.route("/agences/new", methods=["GET", "POST"])
def create_agence():
    if request.method == "POST":
        nom_agence = request.form["nom_agence"]
        adresse = request.form["adresse"]

        agence = Agence(nom_agence=nom_agence, adresse=adresse)
        db.session.add(agence)
        db.session.commit()
        return redirect(url_for("crud.list_agences"))
    return render_template("admin/agences/create.html")

# MODIFIER UNE AGENCE
@crud.route("/agences/edit/<int:id_agence>", methods=["GET", "POST"])
def edit_agence(id_agence):
    agence = Agence.query.get_or_404(id_agence)
    if request.method == "POST":
        agence.nom_agence = request.form["nom_agence"]
        agence.adresse = request.form["adresse"]
        db.session.commit()
        return redirect(url_for("crud.list_agences"))
    return render_template("admin/agences/edit.html", agence=agence)

# SUPPRIMER UNE AGENCE
@crud.route("/agences/delete/<int:id_agence>", methods=["POST"])
def delete_agence(id_agence):
    agence = Agence.query.get_or_404(id_agence)
    db.session.delete(agence)
    db.session.commit()
    return redirect(url_for("crud.list_agences"))


# LISTE DES PERSONNELS
@crud.route("/personnels")
def list_personnels():
    personnels = Personnel.query.all()
    return render_template("admin/personnels/list.html", personnels=personnels)

# CREER UN PERSONNEL
@crud.route("/personnels/new", methods=["GET", "POST"])
def create_personnel():
    agences = Agence.query.all()
    if request.method == "POST":
        nom = request.form["nom"]
        prenom = request.form.get("prenom")
        role = request.form["role"]
        id_agence = request.form.get("id_agence")

        personnel = Personnel(nom=nom, prenom=prenom, role=role, id_agence=id_agence)
        db.session.add(personnel)
        db.session.commit()
        return redirect(url_for("crud.list_personnels"))
    return render_template("admin/personnels/create.html", agences=agences)

# MODIFIER UN PERSONNEL
@crud.route("/personnels/edit/<int:id_personnel>", methods=["GET", "POST"])
def edit_personnel(id_personnel):
    personnel = Personnel.query.get_or_404(id_personnel)
    agences = Agence.query.all()
    if request.method == "POST":
        personnel.nom = request.form["nom"]
        personnel.prenom = request.form.get("prenom")
        personnel.role = request.form["role"]
        personnel.id_agence = request.form.get("id_agence")
        db.session.commit()
        return redirect(url_for("crud.list_personnels"))
    return render_template("admin/personnels/edit.html", personnel=personnel, agences=agences)

# SUPPRIMER UN PERSONNEL
@crud.route("/personnels/delete/<int:id_personnel>", methods=["POST"])
def delete_personnel(id_personnel):
    personnel = Personnel.query.get_or_404(id_personnel)
    db.session.delete(personnel)
    db.session.commit()
    return redirect(url_for("crud.list_personnels"))

# ---------------------------------------------------
#                     ROUTES CLIENTS
# ---------------------------------------------------

# -------------------------------------------------
#        FORMULAIRE WEB : Créer un client
# -------------------------------------------------
@crud.route("/clients/new", methods=["GET"])
def new_client_form():
    return render_template("admin/clients/new_client.html")


@crud.route("/clients/new", methods=["POST"])
def create_client_form():
    nom = request.form.get("nom")
    prenom = request.form.get("prenom")
    telephone = request.form.get("telephone")
    email = request.form.get("email")
    cni = request.form.get("cni")

    client = Client(
        nom=nom,
        prenom=prenom,
        telephone=telephone,
        email=email,
        cni=cni
    )

    db.session.add(client)
    db.session.commit()

    return redirect(url_for("crud.list_clients"))


# -------------------------------------------------
#     PAGE WEB : Liste des clients
# -------------------------------------------------
@crud.route("/clients", methods=["GET"])
def list_clients():
    clients = Client.query.all()
    return render_template("admin/clients/list_clients.html", clients=clients)



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


# ============================
# CRUD TRAJET
# ============================

@crud.route("/trajets")
def trajets_list():
    trajets = Trajet.query.all()
    return render_template("admin/trajets/list.html", trajets=trajets)


@crud.route("/trajets/create", methods=["GET", "POST"])
def trajets_create():
    if request.method == "POST":
        t = Trajet(
            ville_depart=request.form["ville_depart"],
            ville_arrivee=request.form["ville_arrivee"],
            tarif_standard=request.form["tarif_standard"],
            tarif_vip=request.form["tarif_vip"]
        )
        db.session.add(t)
        db.session.commit()
        return redirect("/trajets")

    return render_template("admin/trajets/create.html")


@crud.route("/trajets/<int:id>/edit", methods=["GET", "POST"])
def trajets_edit(id):
    t = Trajet.query.get_or_404(id)

    if request.method == "POST":
        t.ville_depart = request.form["ville_depart"]
        t.ville_arrivee = request.form["ville_arrivee"]
        t.tarif_standard = request.form["tarif_standard"]
        t.tarif_vip = request.form["tarif_vip"]
        db.session.commit()
        return redirect("/trajets")

    return render_template("admin/trajets/edit.html", trajet=t)




# VEHICULES
@crud.route("/vehicules")
def list_vehicules():
    vehicules = Vehicule.query.all()
    return render_template("admin/vehicules/list.html", vehicules=vehicules)

@crud.route("/vehicules/new", methods=["GET", "POST"])
def create_vehicule():
    if request.method == "POST":
        immatriculation = request.form["immatriculation"]
        type_ = request.form["type"]
        capacite = request.form["capacite"]
        statut = request.form.get("statut", "En service")

        vehicule = Vehicule(
            immatriculation=immatriculation,
            type=type_,
            capacite=capacite,
            statut=statut
        )
        db.session.add(vehicule)
        db.session.commit()
        return redirect(url_for("crud.list_vehicules"))

    return render_template("admin/vehicules/create.html")

@crud.route("/vehicules/edit/<string:immatriculation>", methods=["GET", "POST"])
def edit_vehicule(immatriculation):
    vehicule = Vehicule.query.get_or_404(immatriculation)
    if request.method == "POST":
        vehicule.type = request.form["type"]
        vehicule.capacite = request.form["capacite"]
        vehicule.statut = request.form.get("statut", "En service")
        db.session.commit()
        return redirect(url_for("crud.list_vehicules"))

    return render_template("admin/vehicules/edit.html", vehicule=vehicule)

@crud.route("/vehicules/delete/<string:immatriculation>", methods=["POST"])
def delete_vehicule(immatriculation):
    vehicule = Vehicule.query.get_or_404(immatriculation)
    db.session.delete(vehicule)
    db.session.commit()
    return redirect(url_for("crud.list_vehicules"))



# ---------------------
# 1. LISTE DES VOYAGES
# ---------------------
@crud.route("/voyages", methods=["GET"])
def list_voyages():
    voyages = Voyage.query.all()
    return render_template("admin/voyages/list.html", voyages=voyages)


# ---------------------
# 2. FORMULAIRE + CREATE
# ---------------------
@crud.route("/voyages/new", methods=["GET", "POST"])
def create_voyage():
    trajets = Trajet.query.all()
    vehicules = Vehicule.query.all()
    agences = Agence.query.all()

    if request.method == "POST":
        date_depart = request.form.get("date_depart")
        heure_depart = request.form.get("heure_depart")
        id_trajet = request.form.get("id_trajet")
        immatriculation = request.form.get("immatriculation")
        id_agence = request.form.get("id_agence")
        standing = request.form.get("standing")
        places_reservees = request.form.get("places_reservees", 0)

        voyage = Voyage(
            date_depart=date_depart,
            heure_depart=heure_depart,
            id_trajet=id_trajet,
            immatriculation=immatriculation,
            id_agence=id_agence,
            standing=standing,
            places_reservees=places_reservees,
        )
        db.session.add(voyage)
        db.session.commit()
        return redirect(url_for("crud.list_voyages"))

    return render_template("admin/voyages/create.html", trajets=trajets, vehicules=vehicules, agences=agences)


# ---------------------
# 3. UPDATE
# ---------------------
@crud.route("/voyages/edit/<int:id_voyage>", methods=["GET", "POST"])
def edit_voyage(id_voyage):
    voyage = Voyage.query.get_or_404(id_voyage)
    trajets = Trajet.query.all()
    vehicules = Vehicule.query.all()
    agences = Agence.query.all()

    if request.method == "POST":
        voyage.date_depart = request.form.get("date_depart")
        voyage.heure_depart = request.form.get("heure_depart")
        voyage.id_trajet = request.form.get("id_trajet")
        voyage.immatriculation = request.form.get("immatriculation")
        voyage.id_agence = request.form.get("id_agence")
        voyage.standing = request.form.get("standing")
        voyage.places_reservees = request.form.get("places_reservees")

        db.session.commit()
        return redirect(url_for("crud.list_voyages"))

    return render_template("admin/voyages/edit.html", voyage=voyage, trajets=trajets, vehicules=vehicules, agences=agences)


# ---------------------
# 4. DELETE
# ---------------------
@crud.route("/voyages/delete/<int:id_voyage>", methods=["POST"])
def delete_voyage(id_voyage):
    voyage = Voyage.query.get_or_404(id_voyage)
    db.session.delete(voyage)
    db.session.commit()
    return redirect(url_for("crud.list_voyages"))


# ---------------------
# RESERVATIONS
# ---------------------

@crud.route("/reservation", methods=["GET", "POST"])
def reservation():
    # --- PAGE AVEC FORMULAIRE DE RECHERCHE (GET) ---
    if request.method == "GET":
        # Récupérer les paramètres de recherche
        ville_depart = request.args.get("ville_depart")
        ville_arrivee = request.args.get("ville_arrivee")
        date_depart = request.args.get("date_depart")
        passagers = request.args.get("passagers")
        
        # Filtrer les voyages selon les critères
        query = Voyage.query.join(Trajet)
        
        if ville_depart:
            query = query.filter(Trajet.ville_depart.ilike(f"%{ville_depart}%"))
        
        if ville_arrivee:
            query = query.filter(Trajet.ville_arrivee.ilike(f"%{ville_arrivee}%"))
        
        if date_depart:
            query = query.filter(Voyage.date_depart == date_depart)
        
        voyages = query.all()
        
        return render_template("admin/reservation/form.html", 
                             voyages=voyages,
                             ville_depart=ville_depart,
                             ville_arrivee=ville_arrivee,
                             date_depart=date_depart,
                             passagers=passagers)

    # --- TRAITEMENT FORMULAIRE DE RÉSERVATION (POST) ---
    nom = request.form["nom"]
    prenom = request.form.get("prenom")
    telephone = request.form["telephone"]
    email = request.form.get("email")
    id_voyage = request.form["id_voyage"]
    mode_paiement = request.form["mode"]
    montant = int(request.form["montant"])

    # 1️⃣ Vérifier si le client existe déjà (par téléphone)
    client = Client.query.filter_by(telephone=telephone).first()

    if not client:

        client = Client(
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            email=email,
            password=generate_password_hash("default123"),
            cni="none"
        )
        db.session.add(client)
        db.session.commit()

    # 2️⃣ Créer un paiement
    paiement = Paiement(
        montant=montant,
        date_paiement=datetime.datetime.utcnow(),
        mode=mode_paiement,
        reference_transaction=f"REF-{uuid.uuid4().hex[:10].upper()}"
    )
    db.session.add(paiement)
    db.session.commit()

    # 3️⃣ Récupérer le voyage et incrémenter les places réservées
    voyage = Voyage.query.get(id_voyage)
    if voyage:
        voyage.places_reservees += 1
        db.session.commit()

    # 4️⃣ Créer la réservation
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

    return render_template(
        "admin/reservation/success.html",
        reservation=reservation,
        client=client,
        paiement=paiement
    )
#
# TABLEAU DE BORD
#
@crud.route("/dashboard")
def dashboard():
    total_clients = Client.query.count()
    total_voyages = Voyage.query.count()
    total_reservations = Reservation.query.count()

    return render_template("/admin/dashboard.html",
                           total_clients=total_clients,
                           total_voyages=total_voyages,
                           total_reservations=total_reservations)
