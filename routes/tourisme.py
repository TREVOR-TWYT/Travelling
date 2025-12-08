from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Tourisme, Agence

tourisme_bp = Blueprint('tourisme', __name__, template_folder='../templates/tourisme')

# Liste des circuits
@tourisme_bp.route('/tourisme')
def list_tourisme():
    tours = Tourisme.query.all()
    return render_template('tourisme_list.html', tours=tours)

# Ajouter un circuit
@tourisme_bp.route('/tourisme/ajouter', methods=['GET', 'POST'])
def add_tourisme():
    agences = Agence.query.all()
    if request.method == 'POST':
        tour = Tourisme(
            nom=request.form['nom'],
            description=request.form['description'],
            duree=request.form['duree'],
            prix=request.form['prix'],
            agence_id=request.form['agence_id']
        )
        db.session.add(tour)
        db.session.commit()
        return redirect(url_for('tourisme.list_tourisme'))
    return render_template('tourisme_new.html', agences=agences)

# Modifier un circuit
@tourisme_bp.route('/tourisme/modifier/<int:id>', methods=['GET', 'POST'])
def edit_tourisme(id):
    tour = Tourisme.query.get_or_404(id)
    agences = Agence.query.all()
    if request.method == 'POST':
        tour.nom = request.form['nom']
        tour.description = request.form['description']
        tour.duree = request.form['duree']
        tour.prix = request.form['prix']
        tour.agence_id = request.form['agence_id']
        db.session.commit()
        return redirect(url_for('tourisme.list_tourisme'))
    return render_template('tourisme_edit.html', tour=tour, agences=agences)

# Supprimer un circuit
@tourisme_bp.route('/tourisme/supprimer/<int:id>')
def delete_tourisme(id):
    tour = Tourisme.query.get_or_404(id)
    db.session.delete(tour)
    db.session.commit()
    return redirect(url_for('tourisme.list_tourisme'))

