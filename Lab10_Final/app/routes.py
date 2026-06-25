from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user, login_user, logout_user
from app.models import Task, User, Profile
from flask import current_app as app
from app import db

@app.before_request
def before_request_logging():
    app.logger.debug(f"Request: {request.method} {request.path}")

@app.teardown_request
def log_teardown(exc):
    if exc:
        app.logger.error("Exception caught in teardown", exc_info=exc)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # if User.query.filter_by(username=username).first():
        #     flash("Username already exists", "warning")
        #     return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists", "warning")
            return redirect(url_for("register"))


        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Create empty profile
        profile = Profile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# ------------------- LOGIN -------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        flash("Invalid credentials", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")

# ------------------- LOGOUT -------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

# ------------------- HOME / DASHBOARD -------------------
@app.route("/home")
@login_required
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", tasks=tasks)


# ------------------- CREATE TASK -------------------
@app.route("/task/create", methods=["POST"])
@login_required
def create_task():
    title = request.form.get("title")
    description = request.form.get("description")

    if not title:
        flash("Task title is required.", "warning")
        return redirect(url_for("home"))

    task = Task(title=title, description=description, user_id=current_user.id)
    db.session.add(task)
    db.session.commit()
    flash("Task created successfully!", "success")
    return redirect(url_for("home"))


# ------------------- COMPLETE TASK -------------------
@app.route("/task/<int:task_id>/complete")
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    task.completed = True
    db.session.commit()
    flash("Task marked as complete!", "success")
    return redirect(url_for("home"))


# ------------------- DELETE TASK -------------------
@app.route("/task/<int:task_id>/delete")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted!", "success")
    return redirect(url_for("home"))

# ------------------- VIEW / EDIT PROFILE -------------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile = current_user.profile
    if request.method == "POST":
        full_name = request.form.get("full_name")
        phone = request.form.get("phone")

        profile.full_name = full_name
        profile.phone = phone
        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", profile=profile)

# ------------------- ERROR HANDLERS -------------------
@app.errorhandler(404)
def not_found_error(e):
    app.logger.error("Unhandled Exception: %s", e, exc_info=True)
    return render_template("errors.html", code=404, message="Page Not Found"), 404

@app.errorhandler(500)
def internal_error(e):
    app.logger.error("Unhandled Exception: %s", e, exc_info=True)
    return render_template("errors.html", code=500, message="Internal Server Error"), 500


@app.errorhandler(403)
def forbidden_error(e):
    app.logger.error("Unhandled Exception: %s", e, exc_info=True)
    return render_template("errors.html", code=403, message="Forbidden"), 403


@app.errorhandler(401)
def unauthorized_error(e):
    app.logger.error("Unhandled Exception: %s", e, exc_info=True)
    return render_template("errors.html", code=401, message="Unauthorized Access"), 401
