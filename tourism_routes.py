from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from models import *
from functools import wraps
import datetime
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
                date_paiement=datetime.datetime.utcnow(),
                mode=mode_paiement,
                reference_transaction=f"TOUR-{uuid.uuid4().hex[:10].upper()}"
            )
            db.session.add(paiement)
            db.session.flush()
            
            # Créer la réservation
            reservation = ReservationExcursion(
                num_reservation=f"EXC-{uuid.uuid4().hex[:8].upper()}",
                date_reservation=datetime.datetime.utcnow(),
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
    """Louer un véhicule"""
    vehicule = Vehicule.query.get_or_404(immatriculation)
    client = Client.query.get(session['client_id'])
    
    # Vérifier disponibilité
    location_en_cours = LocationVehicule.query.filter_by(
        immatriculation=immatriculation,
        statut="En cours"
    ).first()
    
    if location_en_cours:
        flash("Ce véhicule n'est pas disponible actuellement", "error")
        return redirect(url_for('tourism.liste_vehicules_location'))
    
    if request.method == "POST":
        try:
            date_debut = request.form.get("date_debut")
            date_fin = request.form.get("date_fin")
            heure_debut = request.form.get("heure_debut", "08:00")
            tarif_journalier = int(request.form.get("tarif_journalier"))
            caution = int(request.form.get("caution"))
            mode_paiement = request.form.get("mode_paiement")
            
            # Calculer le nombre de jours
            debut = datetime.datetime.strptime(date_debut, "%Y-%m-%d")
            fin = datetime.datetime.strptime(date_fin, "%Y-%m-%d")
            nb_jours = (fin - debut).days + 1
            
            if nb_jours < 1:
                flash("La période de location doit être d'au moins 1 jour", "error")
                return redirect(request.url)
            
            montant_total = (tarif_journalier * nb_jours) + caution
            
            # Créer le paiement
            paiement = Paiement(
                montant=montant_total,
                date_paiement=datetime.datetime.utcnow(),
                mode=mode_paiement,
                reference_transaction=f"LOC-{uuid.uuid4().hex[:10].upper()}"
            )
            db.session.add(paiement)
            db.session.flush()
            
            # Créer la location
            location = LocationVehicule(
                num_location=f"LOC-{uuid.uuid4().hex[:8].upper()}",
                date_debut=debut,
                date_fin=fin,
                heure_debut=datetime.datetime.strptime(heure_debut, "%H:%M").time(),
                immatriculation=immatriculation,
                id_client=client.id_client,
                tarif_journalier=tarif_journalier,
                caution=caution,
                montant_total=montant_total,
                statut="En cours",
                id_paiement=paiement.id_paiement
            )
            db.session.add(location)
            db.session.commit()
            
            flash("🎉 Location confirmée!", "success")
            return redirect(url_for('tourism.mes_locations'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur: {e}")
            flash("Erreur lors de la location", "error")
            return redirect(request.url)
    
    return render_template("public/location/louer_vehicule.html", vehicule=vehicule, client=client)


@tourism.route("/mes-locations")
@login_required
def mes_locations():
    """Mes locations de véhicules"""
    client = Client.query.get(session['client_id'])
    locations = LocationVehicule.query.filter_by(id_client=client.id_client).all()
    
    return render_template("public/location/mes_locations.html", locations=locations, client=client)


# ============================================
# ROUTES PUBLIQUES - EXPÉDITION COLIS
# ============================================

@tourism.route("/expedition-colis")
def expedition_colis():
    """Page d'expédition de colis"""
    trajets = Trajet.query.all()
    return render_template("public/expedition/expedition.html", trajets=trajets)


@tourism.route("/expedition/nouveau", methods=["POST"])
@login_required
def creer_expedition():
    """Créer une nouvelle expédition"""
    try:
        client = Client.query.get(session['client_id'])
        
        ville_depart = request.form.get("ville_depart")
        ville_arrivee = request.form.get("ville_arrivee")
        nom_destinataire = request.form.get("nom_destinataire")
        telephone_destinataire = request.form.get("telephone_destinataire")
        nature = request.form.get("nature")
        poids = float(request.form.get("poids", 0))
        frais = int(request.form.get("frais"))
        mode_paiement = request.form.get("mode_paiement")
        
        # Créer le paiement
        paiement = Paiement(
            montant=frais,
            date_paiement=datetime.datetime.utcnow(),
            mode=mode_paiement,
            reference_transaction=f"EXP-{uuid.uuid4().hex[:10].upper()}"
        )
        db.session.add(paiement)
        db.session.flush()
        
        # Créer l'expédition
        num_expedition = f"EXP-{uuid.uuid4().hex[:10].upper()}"
        expedition = Expedition(
            num_expedition=num_expedition,
            date_expedition=datetime.datetime.utcnow(),
            frais=frais,
            nature=nature,
            id_client_expediteur=client.id_client
        )
        db.session.add(expedition)
        db.session.flush()
        
        # Créer le colis
        colis = Colis(
            num_expedition=num_expedition,
            nature=nature,
            quantite=1
        )
        db.session.add(colis)
        
        # Créer le premier statut
        statut = StatutColis(
            num_expedition=num_expedition,
            statut="Enregistré",
            date_heure=datetime.datetime.utcnow(),
            localisation=ville_depart,
            commentaire=f"Colis enregistré pour {ville_arrivee}. Destinataire: {nom_destinataire} ({telephone_destinataire})"
        )
        db.session.add(statut)
        
        db.session.commit()
        
        flash(f"🎉 Expédition créée! Numéro de suivi: {num_expedition}", "success")
        return redirect(url_for('tourism.mes_expeditions'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur: {e}")
        flash("Erreur lors de la création de l'expédition", "error")
        return redirect(url_for('tourism.expedition_colis'))


@tourism.route("/expedition/suivre")
def suivre_expedition():
    """Suivi d'expédition public"""
    num_expedition = request.args.get('num_expedition', '')
    expedition = None
    statuts = []
    
    if num_expedition:
        expedition = Expedition.query.filter_by(num_expedition=num_expedition).first()
        if expedition:
            statuts = StatutColis.query.filter_by(num_expedition=num_expedition).order_by(
                StatutColis.date_heure.desc()
            ).all()
        else:
            flash("Numéro d'expédition non trouvé", "error")
    
    return render_template("public/expedition/suivre.html", expedition=expedition, statuts=statuts, num_expedition=num_expedition)


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
            date_depart=datetime.datetime.strptime(request.form["date_depart"], "%Y-%m-%d"),
            date_retour=datetime.datetime.strptime(request.form["date_retour"], "%Y-%m-%d"),
            heure_depart=datetime.datetime.strptime(request.form["heure_depart"], "%H:%M").time(),
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
            date_heure=datetime.datetime.utcnow(),
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