from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from models import *
from functools import wraps
from datetime import datetime
import uuid

tourism = Blueprint("tourism", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'client_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page', 'error')
            return redirect(url_for('public_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            flash('Accès administrateur requis', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# ROUTES PUBLIQUES - TOURISME
# ============================================

@tourism.route("/tourisme")
def liste_sites():
    """Liste publique des sites touristiques"""
    region = request.args.get('region', '')
    
    query = SiteTouristique.query
    if region:
        query = query.filter(SiteTouristique.region.ilike(f"%{region}%"))
    
    sites = query.all()
    regions = db.session.query(SiteTouristique.region).distinct().all()
    
    return render_template("public/tourisme/sites.html", sites=sites, regions=regions)


@tourism.route("/tourisme/site/<int:id_site>")
def detail_site(id_site):
    """Détail d'un site touristique"""
    site = SiteTouristique.query.get_or_404(id_site)
    excursions = Excursion.query.filter_by(id_site=id_site, statut="Planifiée").all()
    
    return render_template("public/tourisme/detail_site.html", site=site, excursions=excursions)


@tourism.route("/excursions")
def liste_excursions():
    """Liste des excursions disponibles"""
    excursions = Excursion.query.filter_by(statut="Planifiée").all()
    return render_template("public/tourisme/excursions.html", excursions=excursions)


@tourism.route("/excursion/reserver/<int:id_excursion>", methods=["GET", "POST"])
@login_required
def reserver_excursion(id_excursion):
    """Réserver une excursion"""
    excursion = Excursion.query.get_or_404(id_excursion)
    client = Client.query.get(session['client_id'])
    
    if request.method == "POST":
        try:
            nb_adultes = int(request.form.get("nb_adultes", 1))
            nb_enfants = int(request.form.get("nb_enfants", 0))
            mode_paiement = request.form.get("mode_paiement")
            
            # Vérifier la disponibilité
            if (nb_adultes + nb_enfants) > excursion.nb_places_disponibles:
                flash("Pas assez de places disponibles", "error")
                return redirect(url_for('tourism.detail_site', id_site=excursion.id_site))
            
            # Calculer le montant
            montant_total = (nb_adultes * excursion.tarif_par_personne) + (nb_enfants * excursion.tarif_par_personne // 2)
            
            # Créer le paiement
            paiement = Paiement(
                montant=montant_total,
                date_paiement=datetime.utcnow(),
                mode=mode_paiement,
                reference_transaction=f"TOUR-{uuid.uuid4().hex[:10].upper()}"
            )
            db.session.add(paiement)
            db.session.flush()
            
            # Créer la réservation
            reservation = ReservationExcursion(
                num_reservation=f"EXC-{uuid.uuid4().hex[:8].upper()}",
                date_reservation=datetime.utcnow(),
                id_client=client.id_client,
                id_excursion=id_excursion,
                nb_adultes=nb_adultes,
                nb_enfants=nb_enfants,
                montant_total=montant_total,
                statut="Confirmée",
                id_paiement=paiement.id_paiement
            )
            db.session.add(reservation)
            
            # Mettre à jour les places disponibles
            excursion.nb_places_disponibles -= (nb_adultes + nb_enfants)
            
            db.session.commit()
            
            flash("🎉 Réservation excursion confirmée!", "success")
            return redirect(url_for('tourism.mes_excursions'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur: {e}")
            flash("Erreur lors de la réservation", "error")
            return redirect(url_for('tourism.detail_site', id_site=excursion.id_site))
    
    return render_template("public/tourisme/reserver_excursion.html", excursion=excursion, client=client)


@tourism.route("/mes-excursions")
@login_required
def mes_excursions():
    """Mes réservations d'excursions"""
    client = Client.query.get(session['client_id'])
    reservations = ReservationExcursion.query.filter_by(id_client=client.id_client).all()
    
    return render_template("public/tourisme/mes_excursions.html", reservations=reservations, client=client)

# ============================================
# ROUTES ADMIN - MODIFICATION ET SUPPRESSION EXCURSIONS
# ============================================

@tourism.route("/admin/excursion/modifier/<int:id_excursion>", methods=["GET", "POST"])
@admin_required
def admin_modifier_excursion(id_excursion):
    excursion = Excursion.query.get_or_404(id_excursion)
    
    if request.method == "POST":
        try:
            # On met à jour les champs présents dans le HTML
            excursion.nom_excursion = request.form["nom_excursion"]
            excursion.date_depart = datetime.strptime(request.form["date_depart"], "%Y-%m-%d")
            
            # Gestion de l'heure (sécurité si le format change selon le navigateur)
            heure_str = request.form["heure_depart"][:5] 
            excursion.heure_depart = datetime.strptime(heure_str, "%H:%M").time()
            
            excursion.id_site = request.form["id_site"]
            excursion.nb_places_disponibles = int(request.form["nb_places_disponibles"])
            excursion.tarif_par_personne = float(request.form["tarif_par_personne"])
            excursion.statut = request.form["statut"]
            
            # SI tu as besoin de la date_retour, vérifie qu'elle est dans le form
            if "date_retour" in request.form and request.form["date_retour"]:
                excursion.date_retour = datetime.strptime(request.form["date_retour"], "%Y-%m-%d")

            db.session.commit()
            print(">>> MODIFICATION RÉUSSIE ! <<<") # Pour vérifier dans ton terminal
            flash("Excursion mise à jour !", "success")
            return redirect(url_for("tourism.admin_excursions"))
            
        except Exception as e:
            db.session.rollback()
            print(f">>> ERREUR DÉTECTÉE : {e} <<<") # CE PRINT VA TE DIRE LE NOM DU CHAMP MANQUANT
            flash(f"Erreur : {str(e)}", "error")
            
    sites = SiteTouristique.query.all()
    return render_template("admin/tourisme/modifier_excursion.html", excursion=excursion, sites=sites)


@tourism.route("/admin/excursion/supprimer/<int:id_excursion>", methods=["POST"])
@admin_required
def admin_supprimer_excursion(id_excursion):
    """Supprimer une excursion"""
    excursion = Excursion.query.get_or_404(id_excursion)
    try:
        db.session.delete(excursion)
        db.session.commit()
        flash("Excursion supprimée avec succès", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erreur lors de la suppression", "error")
        
    return redirect(url_for("tourism.admin_excursions"))


# ============================================
# ROUTES PUBLIQUES - LOCATION VÉHICULES
# ============================================

@tourism.route("/location-vehicules")
def liste_vehicules_location():
    """Liste des véhicules disponibles à la location"""
    type_vehicule = request.args.get('type', '')
    
    query = Vehicule.query.filter_by(statut="En service")
    if type_vehicule:
        query = query.filter(Vehicule.type.ilike(f"%{type_vehicule}%"))
    
    vehicules = query.all()
    types = db.session.query(Vehicule.type).distinct().all()
    
    # Vérifier la disponibilité
    for vehicule in vehicules:
        # Véhicule indisponible si location en cours
        location_en_cours = LocationVehicule.query.filter_by(
            immatriculation=vehicule.immatriculation,
            statut="En cours"
        ).first()
        vehicule.disponible = not location_en_cours
    
    return render_template("public/location/vehicules.html", vehicules=vehicules, types=types)


@tourism.route("/location/reserver/<string:immatriculation>", methods=["GET", "POST"])
@login_required
def louer_vehicule(immatriculation):
    vehicule = Vehicule.query.get_or_404(immatriculation)
    client = Client.query.get(session['client_id'])
    
    if request.method == "POST":
        try:
            # Récupération des dates depuis le formulaire
            date_debut_str = request.form.get("date_debut")
            date_fin_str = request.form.get("date_fin")
            heure_debut_str = request.form.get("heure_debut", "08:00")
            
            # --- CORRECTION ICI ---
            # On utilise datetime.strptime car 'datetime' est déjà la classe
            debut = datetime.strptime(date_debut_str, "%Y-%m-%d")
            fin = datetime.strptime(date_fin_str, "%Y-%m-%d")
            heure_objet = datetime.strptime(heure_debut_str, "%H:%M").time()
            
            nb_jours = (fin - debut).days + 1
            # -----------------------

            tarif = int(request.form.get("tarif_journalier"))
            caution = int(request.form.get("caution"))
            montant_total = (tarif * nb_jours) + caution

            # Création du paiement
            paiement = Paiement(
                montant=montant_total,
                date_paiement=datetime.now(), # Utilisation directe
                mode=request.form.get("mode_paiement"),
                reference_transaction=f"LOC-{uuid.uuid4().hex[:10].upper()}"
            )
            db.session.add(paiement)
            db.session.flush()
            
            # Création de la location
            location = LocationVehicule(
                num_location=f"LOC-{uuid.uuid4().hex[:8].upper()}",
                date_debut=debut,
                date_fin=fin,
                heure_debut=heure_objet,
                immatriculation=immatriculation,
                id_client=client.id_client,
                tarif_journalier=tarif,
                caution=caution,
                montant_total=montant_total,
                statut="En cours",
                id_paiement=paiement.id_paiement
            )
            db.session.add(location)

            # Mise à jour du véhicule
            vehicule.statut = "Loué"
            
            db.session.commit()
            flash("🎉 Location confirmée !", "success")
            return redirect(url_for('tourism.mes_locations'))

        except Exception as e:
            db.session.rollback()
            # C'est ce print qui a généré ton log d'erreur
            print(f"Erreur détaillée : {e}") 
            flash("Une erreur interne est survenue lors de la réservation.", "error")
            
    return render_template("public/location/louer_vehicule.html", vehicule=vehicule, client=client)


@tourism.route("/mes-locations")
@login_required
def mes_locations():
    """Mes locations de véhicules"""
    client = Client.query.get(session['client_id'])
    locations = LocationVehicule.query.filter_by(id_client=client.id_client).all()
    
    return render_template("public/location/mes_locations.html", locations=locations, client=client)

@tourism.route("/location/annuler/<string:num_location>")
@login_required
def annuler_location(num_location):
    # CORRECTION : On cherche par la colonne num_location, pas par l'ID primaire
    location = LocationVehicule.query.filter_by(num_location=num_location).first_or_404()
    
    if location.id_client != session['client_id']:
        flash("Action non autorisée.", "error")
        return redirect(url_for('tourism.mes_locations'))

    if location.statut == "En cours":
        vehicule = Vehicule.query.get(location.immatriculation)
        if vehicule:
            vehicule.statut = "En service"
        
        location.statut = "Annulée"
        db.session.commit()
        flash(f"La location {num_location} a été annulée.", "success")
    
    return redirect(url_for('tourism.mes_locations'))

@tourism.route("/location/rendre/<string:num_location>")
@login_required
def rendre_location(num_location):
    # CORRECTION : On utilise filter_by ici aussi
    location = LocationVehicule.query.filter_by(num_location=num_location).first_or_404()
    
    if location.id_client != session['client_id']:
        flash("Action non autorisée.", "error")
        return redirect(url_for('tourism.mes_locations'))

    if location.statut == "En cours":
        vehicule = Vehicule.query.get(location.immatriculation)
        if vehicule:
            vehicule.statut = "En service"
        
        location.statut = "Terminée"
        db.session.commit()
        flash(f"Véhicule {location.immatriculation} rendu avec succès.", "success")
    
    return redirect(url_for('tourism.mes_locations'))

# ============================================
# ROUTES PUBLIQUES - EXPÉDITION COLIS
# ============================================

@tourism.route("/expedition-colis")
def expedition_colis():
    """Page d'expédition de colis"""
    trajets = Trajet.query.all()
    return render_template("public/expedition/expedition.html", trajets=trajets)


from flask import session # <--- Assure-toi que session est importé ici
# Pas besoin d'importer current_user

@tourism.route("/expedition/nouveau", methods=["POST"])
@login_required  # Ton décorateur perso
def creer_expedition():
    try:
        # Récupération des données
        ville_depart = request.form.get("ville_depart")
        ville_arrivee = request.form.get("ville_arrivee")
        nom_destinataire = request.form.get("nom_destinataire")
        tel_destinataire = request.form.get("telephone_destinataire")
        nature = request.form.get("nature")
        frais = int(request.form.get("frais", 0))
        
        # 1. Création de l'expédition
        num_expedition = f"EXP-{uuid.uuid4().hex[:10].upper()}"
        
        expedition = Expedition(
            num_expedition=num_expedition,
            date_expedition=datetime.utcnow(), 
            frais=frais,
            nature=nature,
            # C'EST ICI LE CHANGEMENT : On utilise session['client_id']
            id_client_expediteur=session['client_id'], 
            id_voyage=None
        )
        db.session.add(expedition)
        db.session.flush()
        
        # 2. Création du Colis
        colis = Colis(
            num_expedition=num_expedition,
            nature=nature,
            quantite=1 
        )
        db.session.add(colis)
        
        # 3. Création du statut (avec les infos destinataire en commentaire)
        info_destinataire = f"Destinataire: {nom_destinataire} ({tel_destinataire}) - De {ville_depart} à {ville_arrivee}"
        
        statut = StatutColis(
            num_expedition=num_expedition,
            statut="Enregistré",
            date_heure=datetime.utcnow(),
            localisation=ville_depart,
            commentaire=info_destinataire
        )
        db.session.add(statut)
        
        db.session.commit()
        
        flash(f"🎉 Expédition créée ! Suivi: {num_expedition}", "success")
        return redirect(url_for('tourism.mes_expeditions'))

    except Exception as e:
        db.session.rollback()
        print(f"ERREUR SQL: {e}")
        flash(f"Erreur: {e}", "error")
        return redirect(url_for('tourism.expedition_colis'))


@tourism.route("/expedition/suivre")
def suivre_expedition():
    """Suivi d'expédition public"""
    raw_num = request.args.get('num_expedition', '')
    
    expedition = None
    statuts = []
    
    # NETTOYAGE : Enlève les espaces et force les majuscules
    num_search = raw_num.strip().upper() if raw_num else ""
    
    if num_search: 
        # On cherche avec le numéro nettoyé
        expedition = Expedition.query.filter_by(num_expedition=num_search).first()
        
        if expedition:
            statuts = StatutColis.query.filter_by(num_expedition=num_search).order_by(
                StatutColis.date_heure.desc()
            ).all()
        else:
            flash(f"Le numéro {num_search} est introuvable.", "error")
            print(f"DEBUG: {num_search} n'est pas dans la base de données.")
    
    return render_template("public/expedition/suivre.html", expedition=expedition, statuts=statuts, num_expedition=num_search)

@tourism.route("/admin/expedition/modifier/<string:num_expedition>", methods=["GET", "POST"])
@admin_required
def admin_modifier_expedition(num_expedition):
    expedition = Expedition.query.get_or_404(num_expedition)
    
    if request.method == "POST":
        expedition.nature = request.form.get("nature")
        expedition.frais = request.form.get("frais")
        # Tu peux ajouter d'autres champs ici
        db.session.commit()
        flash("Détails de l'expédition mis à jour", "success")
        return redirect(url_for("tourism.admin_expeditions"))
    
    return render_template("admin/expedition/modifier_expedition.html", expedition=expedition)


@tourism.route("/mes-expeditions")
@login_required
def mes_expeditions():
    """Mes expéditions"""
    client = Client.query.get(session['client_id'])
    expeditions = Expedition.query.filter_by(id_client_expediteur=client.id_client).all()
    
    # Récupérer le dernier statut pour chaque expédition
    for exp in expeditions:
        exp.dernier_statut = StatutColis.query.filter_by(
            num_expedition=exp.num_expedition
        ).order_by(StatutColis.date_heure.desc()).first()
    
    return render_template("public/expedition/mes_expeditions.html", expeditions=expeditions, client=client)


# ============================================
# ROUTES ADMIN - TOURISME
# ============================================

@tourism.route("/admin/sites-touristiques")
@admin_required
def admin_sites():
    print(" >>> JE SUIS DANS LA FONCTION ADMIN_SITES <<< ")
    """Gestion des sites touristiques"""
    sites = SiteTouristique.query.all()
    return render_template("admin/tourisme/sites.html", sites=sites)


@tourism.route("/admin/site/nouveau", methods=["GET", "POST"])
@admin_required
def admin_creer_site():
    """Créer un site touristique"""
    if request.method == "POST":
        site = SiteTouristique(
            nom_site=request.form["nom_site"],
            ville=request.form["ville"],
            region=request.form.get("region"),
            description=request.form.get("description"),
            tarif_adulte=request.form["tarif_adulte"],
            tarif_enfant=request.form.get("tarif_enfant"),
            image_url=request.form.get("image_url"),
            coordonnees_gps=request.form.get("coordonnees_gps")
        )
        db.session.add(site)
        db.session.commit()
        flash("Site touristique créé!", "success")
        return redirect(url_for("tourism.admin_sites"))
    
    return render_template("admin/tourisme/creer_site.html")

# ============================================
# ROUTES ADMIN - MODIFICATION ET SUPPRESSION
# ============================================

@tourism.route("/admin/site/modifier/<int:id_site>", methods=["GET", "POST"])
@admin_required
def admin_modifier_site(id_site):
    """Modifier un site touristique existant"""
    site = SiteTouristique.query.get_or_404(id_site)
    
    if request.method == "POST":
        site.nom_site = request.form["nom_site"]
        site.ville = request.form["ville"]
        site.region = request.form.get("region")
        site.description = request.form.get("description")
        site.tarif_adulte = request.form["tarif_adulte"]
        site.tarif_enfant = request.form.get("tarif_enfant")
        site.image_url = request.form.get("image_url")
        site.coordonnees_gps = request.form.get("coordonnees_gps")
        
        try:
            db.session.commit()
            flash(f"Le site '{site.nom_site}' a été mis à jour !", "success")
            return redirect(url_for("tourism.admin_sites"))
        except Exception as e:
            db.session.rollback()
            flash("Erreur lors de la modification", "error")
            
    return render_template("admin/tourisme/modifier_site.html", site=site)


@tourism.route("/admin/site/supprimer/<int:id_site>", methods=["POST"])
@admin_required
def admin_supprimer_site(id_site):
    """Supprimer un site touristique"""
    site = SiteTouristique.query.get_or_404(id_site)
    try:
        db.session.delete(site)
        db.session.commit()
        flash("Site supprimé avec succès", "success")
    except Exception as e:
        db.session.rollback()
        flash("Impossible de supprimer ce site (il est peut-être lié à des excursions)", "error")
        
    return redirect(url_for("tourism.admin_sites"))


@tourism.route("/admin/excursions")
@admin_required
def admin_excursions():
    """Gestion des excursions"""
    excursions = Excursion.query.all()
    return render_template("admin/tourisme/excursions.html", excursions=excursions)


@tourism.route("/admin/excursion/nouvelle", methods=["GET", "POST"])
@admin_required
def admin_creer_excursion():
    """Créer une excursion"""
    if request.method == "POST":
        excursion = Excursion(
            nom_excursion=request.form["nom_excursion"],
            date_depart=datetime.strptime(request.form["date_depart"], "%Y-%m-%d"),
            date_retour=datetime.strptime(request.form["date_retour"], "%Y-%m-%d"),
            heure_depart=datetime.strptime(request.form["heure_depart"], "%H:%M").time(),
            id_site=request.form["id_site"],
            id_agence=request.form.get("id_agence"),
            immatriculation=request.form.get("immatriculation"),
            nb_places_disponibles=request.form["nb_places_disponibles"],
            tarif_par_personne=request.form["tarif_par_personne"],
            statut="Planifiée"
        )
        db.session.add(excursion)
        db.session.commit()
        flash("Excursion créée!", "success")
        return redirect(url_for("tourism.admin_excursions"))
    
    sites = SiteTouristique.query.all()
    agences = Agence.query.all()
    vehicules = Vehicule.query.filter_by(statut="En service").all()
    
    return render_template("admin/tourisme/creer_excursion.html", sites=sites, agences=agences, vehicules=vehicules)

@tourism.route("/admin/excursion/detail/<int:id_excursion>")
@admin_required
def admin_detail_excursion(id_excursion):
    """Voir les détails d'une excursion et les réservations associées"""
    excursion = Excursion.query.get_or_404(id_excursion)
    # Récupérer les réservations pour cette excursion
    reservations = ReservationExcursion.query.filter_by(id_excursion=id_excursion).all()
    
    return render_template("admin/tourisme/detail_excursion.html", 
                           excursion=excursion, 
                           reservations=reservations)


# ============================================
# ROUTES ADMIN - EXPÉDITIONS
# ============================================

@tourism.route("/admin/expeditions")
@admin_required
def admin_expeditions():
    """Gestion des expéditions"""
    expeditions = Expedition.query.all()
    for exp in expeditions:
        exp.dernier_statut = StatutColis.query.filter_by(
            num_expedition=exp.num_expedition
        ).order_by(StatutColis.date_heure.desc()).first()
    
    return render_template("admin/expedition/expeditions.html", expeditions=expeditions)


@tourism.route("/admin/expedition/<string:num_expedition>/statut", methods=["POST"])
@admin_required
def admin_update_statut(num_expedition):
    """Mettre à jour le statut d'une expédition"""
    try:
        statut = StatutColis(
            num_expedition=num_expedition,
            statut=request.form["statut"],
            date_heure=datetime.utcnow(),
            localisation=request.form.get("localisation"),
            commentaire=request.form.get("commentaire")
        )
        db.session.add(statut)
        db.session.commit()
        flash("Statut mis à jour!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erreur lors de la mise à jour", "error")
    
    return redirect(url_for("tourism.admin_expeditions"))