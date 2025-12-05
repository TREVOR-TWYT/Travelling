from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.models import db   

migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Configuration DB
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://trevor:TREFRIED1707@localhost/travelling"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialisation
    db.init_app(app)
    migrate.init_app(app, db)  

    # Charger les modèles
    from . import models

    # Blueprints
    from .crud_routes import crud
    app.register_blueprint(crud)

    @app.route("/")
    def home():
        return "<h1>Application Travelling opérationnelle !</h1>"

    return app
