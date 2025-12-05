from flask import Blueprint, render_template, request, redirect, url_for
from models_location import db, Vehicule

location_bp = Blueprint('location', __name__, template_folder='templates/location')

@location_bp.route('/vehicules')
def liste_vehicules():
    vehicules = Vehicule.query.all()
    return render_template('liste.html', vehicules=vehicules)

@location_bp.route('/vehicules/ajouter', methods=['GET','POST'])
def ajouter_vehicule():
    if request.method == 'POST':
        marque = request.form['marque']
        modele = request.form['modele']
        prix_jour = float(request.form['prix_jour'])
        vehicule = Vehicule(marque=marque, modele=modele, prix_jour=prix_jour)
        db.session.add(vehicule)
        db.session.commit()
        return redirect(url_for('location.liste_vehicules'))
    return render_template('ajouter.html')

@location_bp.route('/vehicules/modifier/<int:id>', methods=['GET','POST'])
def modifier_vehicule(id):
    vehicule = Vehicule.query.get_or_404(id)
    if request.method == 'POST':
        vehicule.marque = request.form['marque']
        vehicule.modele = request.form['modele']
        vehicule.prix_jour = float(request.form['prix_jour'])
        db.session.commit()
        return redirect(url_for('location.liste_vehicules'))
    return render_template('modifier.html', vehicule=vehicule)

@location_bp.route('/vehicules/supprimer/<int:id>')
def supprimer_vehicule(id):
    vehicule = Vehicule.query.get_or_404(id)
    db.session.delete(vehicule)
    db.session.commit()
    return redirect(url_for('location.liste_vehicules'))
