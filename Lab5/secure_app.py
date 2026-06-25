from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecurekey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secure_users.db'
db = SQLAlchemy(app)


# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), nullable=False, unique=True)
#     password = db.Column(db.String(150), nullable=False)
#     role = db.Column(db.String(50), nullable=False)

# Initialize the DB with sample data
@app.before_request
def create_tables():
    db.create_all()
    if not User.query.first():
        admin = User(username="ali", password="admin123", role="admin")
        user1 = User(username="mohammed", password="12345", role="user")

        db.session.add(admin)
        db.session.add(user1)
        db.session.commit()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form_username = request.form.get("username")
        form_password = request.form.get("password")

        user = User.query.filter_by(username=form_username, password=form_password).first()

        # user = User.query.filter_by(username= form_username, password=form_password).first()
        if user:
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            return "Login failed. Invalid credentials!"

    return render_template("login_secure.html")


@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        return redirect(url_for("login"))

    if session['role'] == 'admin':
        users = User.query.with_entities(User.username, User.role, User.password).all()
        return render_template("dashboard_secure.html", username=session['username'], role=session['role'], users=users)
    else:
        return render_template("dashboard_secure.html", username=session['username'], role=session['role'], users=None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
