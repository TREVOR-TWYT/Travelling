<<<<<<< Updated upstream
from flask import Flask
from models import db
from crud_routes import crud

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://trevor:TREFRIED1707@localhost/travelling"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
=======
from flask import Flask, render_template;
from app.models import db
from app.crud_routes import crud

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://trevor:TREFRIED1707@localhost/travelling'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
>>>>>>> Stashed changes

db.init_app(app)

# Register blueprint
app.register_blueprint(crud)

@app.route("/")
def index():
    return "<h1>Application Travelling opérationnelle !</h1>"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")
