from flask import Blueprint, render_template, request, redirect, url_for
from models_tourisme import db, Tourisme

tourisme_bp = Blueprint('tourisme', __name__, template_folder='templates/tourisme')

@tourisme_bp.route('/tourisme')
def liste_tourisme():
    tours = Tourisme.query.all()
    return render_template('liste.html', tours=tours)

@tourisme_bp.route('/tourisme/ajouter', methods=['GET','POST'])
def ajouter_tourisme():
    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        prix = request.form['prix']
        tour = Tourisme(nom=nom, description=description, prix=float(prix))
        db.session.add(tour)
        db.session.commit()
        return redirect(url_for('tourisme.liste_tourisme'))
    return render_template('ajouter.html')

@tourisme_bp.route('/tourisme/modifier/<int:id>', methods=['GET','POST'])
def modifier_tourisme(id):
    tour = Tourisme.query.get_or_404(id)
    if request.method == 'POST':
        tour.nom = request.form['nom']
        tour.description = request.form['description']
        tour.prix = float(request.form['prix'])
        db.session.commit()
        return redirect(url_for('tourisme.liste_tourisme'))
    return render_template('modifier.html', tour=tour)

@tourisme_bp.route('/tourisme/supprimer/<int:id>')
def supprimer_tourisme(id):
    tour = Tourisme.query.get_or_404(id)
    db.session.delete(tour)
    db.session.commit()
    return redirect(url_for('tourisme.liste_tourisme'))
