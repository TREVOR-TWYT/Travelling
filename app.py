from flask import Flask, render_template;
from app.models import db
from app.crud_routes import crud

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://trevor:TREFRIED1707@localhost/travelling'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register blueprint
app.register_blueprint(crud)

@app.route("/")
def index():
    return render_template("public/index.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")
