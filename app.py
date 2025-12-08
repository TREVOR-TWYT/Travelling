import sys
import os

# Ajouter le dossier du projet au chemin de recherche des modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, render_template, redirect
from models import db
from crud_routes import crud 

from routes.locations import locations_bp
from routes.tourisme import tourisme_bp

app = Flask(__name__)

# Connexion à PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://debora:ndenoka@localhost:5432/travellingdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de la base

db.init_app(app)

# Register blueprint
app.register_blueprint(crud)
app.register_blueprint(locations_bp)      # Module Locations
app.register_blueprint(tourisme_bp)       # Module Tourisme

@app.route("/")
def index():
    return render_template("layout.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")



