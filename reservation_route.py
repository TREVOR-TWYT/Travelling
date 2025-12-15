@reservation_bp.route("/reservation", methods=["POST"])
def reserver_voyage():
    nom = request.form.get("nom")
    prenom = request.form.get("prenom")
    telephone = request.form.get("telephone")
    email = request.form.get("email")
    id_voyage = request.form.get("id_voyage")
    montant = request.form.get("montant")
    mode = request.form.get("mode")

    # ------------------------
    # 1. Vérifier ou créer le client
    # ------------------------
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

    # ------------------------
    # 2. Générer un paiement
    # ------------------------
    paiement = Paiement(
        montant=montant,
        date_paiement=datetime.datetime.now(),
        mode=mode,
        reference_transaction=str(uuid.uuid4())[:12]
    )
    db.session.add(paiement)
    db.session.commit()

    # ------------------------
    # 3. Créer la réservation
    # ------------------------
    reservation = Reservation(
        num_reservation=str(uuid.uuid4())[:10],
        date_reservation=datetime.datetime.now(),
        statut="Confirmée",
        id_client=client.id_client,
        id_voyage=id_voyage,
        id_paiement=paiement.id_paiement
    )

    db.session.add(reservation)
    db.session.commit()

    return {
        "message": "Réservation effectuée avec succès",
        "num_reservation": reservation.num_reservation,
        "client": client.nom + " " + (client.prenom or ""),
        "voyage": id_voyage,
        "montant": montant
    }
