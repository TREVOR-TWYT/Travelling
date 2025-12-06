from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuration DB
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:azerty@localhost/Travelling'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Import des modèles pour que SQLAlchemy les charge
    from . import models

    # Enregistrement des blueprints
    from .crud_routes import crud
    app.register_blueprint(crud)

    @app.route("/")
    def home():
        return "<h1>Application Mboa travel opérationnelle !</h1>"

    return app
