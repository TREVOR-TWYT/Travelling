from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Location, Client, Vehicule

locations_bp = Blueprint('locations', __name__, template_folder='../templates/locations')

# Liste des locations
@locations_bp.route('/locations')
def list_locations():
    locations = Location.query.all()
    return render_template('locations_list.html', locations=locations)

# Ajouter une location
@locations_bp.route('/locations/ajouter', methods=['GET', 'POST'])
def add_location():
    clients = Client.query.all()
    vehicules = Vehicule.query.all()
    if request.method == 'POST':
        location = Location(
            client_id=request.form['client_id'],
            vehicule_id=request.form['vehicule_id'],
            date_debut=request.form['date_debut'],
            date_fin=request.form['date_fin'],
            prix_total=request.form['prix_total'],
            statut=request.form.get('statut', 'En cours')
        )
        db.session.add(location)
        db.session.commit()
        return redirect(url_for('locations.list_locations'))
    return render_template('locations_new.html', clients=clients, vehicules=vehicules)

# Modifier une location
@locations_bp.route('/locations/modifier/<int:id>', methods=['GET', 'POST'])
def edit_location(id):
    location = Location.query.get_or_404(id)
    clients = Client.query.all()
    vehicules = Vehicule.query.all()
    if request.method == 'POST':
        location.client_id = request.form['client_id']
        location.vehicule_id = request.form['vehicule_id']
        location.date_debut = request.form['date_debut']
        location.date_fin = request.form['date_fin']
        location.prix_total = request.form['prix_total']
        location.statut = request.form['statut']
        db.session.commit()
        return redirect(url_for('locations.list_locations'))
    return render_template('locations_edit.html', location=location, clients=clients, vehicules=vehicules)

# Supprimer une location
@locations_bp.route('/locations/supprimer/<int:id>')
def delete_location(id):
    location = Location.query.get_or_404(id)
    db.session.delete(location)
    db.session.commit()
    return redirect(url_for('locations.list_locations'))

