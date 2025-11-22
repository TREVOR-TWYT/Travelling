from app import create_app, db
from app.models import Client
from werkzeug.security import generate_password_hash

# Crée une instance de l'app Flask
app = create_app()

with app.app_context():
    clients = Client.query.all()
    for c in clients:
        if not getattr(c, "password", None):
            # Met un mot de passe temporaire (à changer ensuite)
            c.password = generate_password_hash("changeme")
    db.session.commit()

print("Tous les clients ont maintenant un mot de passe.")
