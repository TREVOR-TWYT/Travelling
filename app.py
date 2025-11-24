from flask import Flask, request, render_template, redirect, session
from models import db
from crud_routes import crud

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:azerty@localhost/Travelling'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register blueprint
app.register_blueprint(crud)

#route pour la page d'acceuil
@app.route("/")
def index():
    return render_template("acceuil.html")

@app.route("/admin/layout")
def admin():
    return render_template("/admin/layout.html")

@app.route("/public/index")
def public_index():
    return render_template("/public/index.html")

@app.route("/public/index/reservation")
def public_reservation():
    return render_template("/public/reservation.html")

@app.route("/public/index/login")
def public_login():
    return render_template("/public/login.html")

@app.route("/public/index/contact")
def public_contact():
    return render_template("/public/contact.html")

@app.route("/public/index/register")
def public_register():
    return render_template("/public/register.html")

@app.route("/public/index/tableau_de_bord")
def public_dashboard():
    return render_template("/public/dashboard.html")

# login route

app.secret_key = "super_clef_secrete_à_modifier"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/layout")  # Page secrète admin
        
        return render_template("admin/login_admin.html", error="Identifiants incorrects")

    return render_template("admin/login_admin.html")




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")
