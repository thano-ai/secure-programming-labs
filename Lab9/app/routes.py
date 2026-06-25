from flask import render_template, request, redirect, url_for, session, flash, abort
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required
from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app
import secrets
from datetime import datetime

@app.before_request
def verify_session():
    # --- optional: IP / UA binding you had (note: can be brittle on some networks)
    if 'ip' in session and session['ip'] != request.remote_addr:
        session.clear()
        abort(403)
    if 'ua' in session and session['ua'] != request.headers.get('User-Agent'):
        session.clear()
        abort(403)

    # If user is logged in, ensure session token matches DB and is not expired
    if current_user.is_authenticated:
        token = session.get('session_token')
        # mismatch or missing token => reject/force logout
        if not token or token != current_user.active_session_token:
            logout_user()
            session.clear()
            abort(403)

        # check server-side expiry
        if current_user.active_session_expiry and current_user.active_session_expiry < datetime.utcnow():
            # session expired server-side: clear DB state and force logout
            current_user.active_session_token = None
            current_user.active_session_expiry = None
            db.session.commit()
            logout_user()
            session.clear()
            # abort(403)

        # extend sliding expiry on activity (optional; keeps the session alive while active)
        # current_user.active_session_expiry = datetime.utcnow() + 120
        # db.session.commit()
        # session.modified = True


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            # Option B: Reject new login **if** there is an active non-expired session
            # Compute expiry for the new session:
            token = secrets.token_hex(32)
            expiry = datetime.utcnow() + app.permanent_session_lifetime

            # Atomic-ish update: set active_session_* only if currently NULL (reduces race)
            updated = User.query.filter(User.id == user.id, User.active_session_token == None).update({
                User.active_session_token: token,
                User.active_session_expiry: expiry
            })
            if updated == 0:
                # No rows updated -> there is already an active token (or a race where someone just set it)
                # But we should still check if that token is expired (rare path). Re-fetch user:
                db.session.commit()
                user_refreshed = User.query.get(user.id)
                if user_refreshed.is_session_active():
                    flash("This account is already logged in from another device. Please logout there first.")
                    return redirect(url_for('login'))
                else:
                    # token existed but expired; try again (set token)
                    token = secrets.token_hex(32)
                    expiry = datetime.utcnow() + app.permanent_session_lifetime
                    User.query.filter(User.id == user.id).update({
                        User.active_session_token: token,
                        User.active_session_expiry: expiry
                    })
                    db.session.commit()
            else:
                # we successfully created the server-side session
                db.session.commit()

            # Re-query user so current_user reflects DB state
            user = User.query.get(user.id)

            # create client session
            session.clear()  # mitigate session fixation
            login_user(user, remember=False, fresh=True)

            # store server token in client session for verification on each request
            session['session_token'] = token
            session['ip'] = request.remote_addr
            session['ua'] = request.headers.get('User-Agent')
            session.permanent = True
            session.modified = True

            return redirect(url_for('dashboard'))

        flash("Invalid credentials")
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)


@app.route('/logout')
@login_required
def logout():
    # clear server-side active session token so future logins are allowed
    current_user.active_session_token = None
    current_user.active_session_expiry = None
    db.session.commit()

    logout_user()
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("User created! Please login.")
            return redirect(url_for('login'))
    return render_template('register.html')


# @app.route('/whoami')
# def whoami():
#     from flask import jsonify
#     return jsonify(
#         authenticated=current_user.is_authenticated,
#         user=getattr(current_user, "username", None),
#         session_user=session.get("session_token")
#     )

@app.route('/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Verify old password
        if not check_password_hash(current_user.password, old_password):
            flash("Old password is incorrect.")
            return redirect(url_for('change_password'))

        # Confirm new password match
        if new_password != confirm_password:
            flash("New passwords do not match.")
            return redirect(url_for('change_password'))

        # Update password securely
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        flash("Password changed successfully! Please log in again.")

        # Optional: logout to force re-login
        # logout_user()
        return redirect(url_for('logout'))

    return render_template('change_password.html')
