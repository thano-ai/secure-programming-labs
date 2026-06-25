from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, argon2, User
from cryptography.fernet import Fernet
from itsdangerous import URLSafeSerializer

app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)
argon2.init_app(app)

fernet = Fernet(app.config['ENCRYPTION_KEY'])
serializer = URLSafeSerializer(app.config['SECRET_KEY'])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"   # redirect here if not logged in

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        ssn = request.form["ssn"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))

        ssn_encrypt = fernet.encrypt(ssn.encode())
        user = User(username=username, ssn_encrypted=ssn_encrypt)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            session["token"] = serializer.dumps(user.id)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard", token=session["token"]))
        flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/dashboard/<token>")
@login_required
def dashboard(token):
    try:
        user_id = serializer.loads(token)
    except:
        flash("Invalid or tampered token.", "danger")
        return redirect(url_for("login"))

    if current_user.id != user_id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    ssn = fernet.decrypt(current_user.ssn_encrypted).decode() if current_user.ssn_encrypted else "N/A"
    return render_template("dashboard.html", user=current_user, ssn=ssn)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
