from flask import Blueprint, request, jsonify
from .models import db, Agence, Client, Trajet

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
