from flask import Blueprint, request, jsonify,render_template,request, redirect, session, url_for,flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import*
from datetime import datetime
import random,string
import uuid

# ---------------------------------------------------
#                     COTÉ ADMIN
# ---------------------------------------------------

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

@crud.route("/reservationAdmin", methods=["GET", "POST"])
def reservationAdmin():
    # --- PAGE AVEC FORMULAIRE ---
    if request.method == "GET":
     
        trajets = Trajet.query.all()
        return render_template("admin/reservation/form.html", trajets=trajets)

    # --- TRAITEMENT FORMULAIRE ---
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
            email=email
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

    # 3️⃣ Créer la réservation
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
@crud.route("/dashboardAdmin")
def dashboardAdmin():
    total_clients = Client.query.count()
    total_voyages = Voyage.query.count()
    total_reservations = Reservation.query.count()

    return render_template("/admin/dashboard.html",
                           total_clients=total_clients,
                           total_voyages=total_voyages,
                           total_reservations=total_reservations)



# ---------------------------------------------------
#                     COTÉ CLIENT
# ---------------------------------------------------


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
@crud.route("/dashboardClient")
@login_required
def dashboardClient():
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
def reservatione():
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



# crud.py

@crud.route("/reservationClient", methods=["GET"])
def reservation():
    ville_depart = request.args.get("ville_depart", "")
    ville_arrivee = request.args.get("ville_arrivee", "")
    
    # ----------------------------------------------------
    # MODIFICATION CLÉ : RETIRER LA VÉRIFICATION DE SESSION
    # ----------------------------------------------------
    # if "client_id" not in session:
    #     flash("Veuillez vous connecter ou vous inscrire pour rechercher un trajet.", "warning")
    #     voyages = []  # aucun résultat affiché
    #     return render_template("public/reservation.html", voyages=voyages)

    voyages = []
    
    # La recherche s'effectue même si le client n'est pas connecté
    if ville_depart and ville_arrivee:
        # Si client connecté, effectuer la recherche
        voyages = Voyage.query.join(Voyage.trajet) # Utilisez .join() et non .has() si possible
        
        voyages = voyages.filter(
            Trajet.ville_depart == ville_depart,
            Trajet.ville_arrivee == ville_arrivee
        ).all()
        
    return render_template("public/reservation.html", 
                           voyages=voyages, 
                           recherche_effectuee=bool(ville_depart and ville_arrivee))


# -----------------------------
# 2. SELECTION DES OPTIONS ET CALCUL DU PRIX (POST)
# -----------------------------
# Route pour gérer la sélection d'un voyage et le calcul dynamique
# crud.py

@crud.route("/selection_options/<int:id_voyage>", methods=["GET", "POST"])
def selection_options(id_voyage):
    
    # ----------------------------------------------------
    # MODIFICATION CLÉ : Autoriser l'accès sans connexion
    # ----------------------------------------------------
    voyage = Voyage.query.get_or_404(id_voyage)
    
    if request.method == "POST":
        # ... (Logique de calcul du prix total reste la même) ...
        # ...
        
        # Stockez les données dans la session pour les étapes suivantes
        session['reservation_options'] = {
            'id_voyage': id_voyage,
            'nombre_places': nombre_places,
            'standing': standing,
            'prix_total': prix_total
        }
        
        # Redirection vers une nouvelle étape : Saisie des informations client
        return redirect(url_for('crud.saisie_client_info'))

    # Logique GET : Afficher le formulaire de sélection
    return render_template("public/selection_form.html", voyage=voyage)


#saisie des informations client (invité ou connecté)

@crud.route("/saisie_client_info", methods=["GET", "POST"])
def saisie_client_info():
    if 'reservation_options' not in session:
        flash("Veuillez d'abord sélectionner un voyage.", "warning")
        return redirect(url_for('crud.reservation'))

    if request.method == "POST":
        # Tentative de connexion (si l'utilisateur a un compte)
        if 'login_email' in request.form:
            # Code pour vérifier les identifiants et définir session['client_id']
            # Si succès :
            # session['client_id'] = client_trouve.id_client
            pass # Poursuivre vers le paiement

        # Réservation Invité (récupération des données)
        else:
            nom = request.form.get("nom")
            prenom = request.form.get("prenom")
            telephone = request.form.get("telephone")
            cni = request.form.get("cni")
            email = request.form.get("email")

            # ------------------------------------------------------------------
            # CRÉATION DU CLIENT DANS LA BDD (OU RÉCUPÉRATION SI CNI/TEL EXISTE)
            # ------------------------------------------------------------------
            client = Client.query.filter_by(CNI=cni).first()
            if not client:
                # Créer un nouveau client "Invité" dans la BDD
                client = Client(nom=nom, prenom=prenom, telephone=telephone, cni=cni, email=email)
                db.session.add(client)
                db.session.commit()
            
            # Stocker l'ID du client (qu'il soit nouveau ou existant) dans la session
            session['client_id_temp'] = client.id_client
        
        # Après avoir identifié ou créé le client, passer à l'étape du siège/paiement
        return redirect(url_for('crud.choix_sieges_et_paiement'))

    return render_template("public/saisie_client_info.html")

