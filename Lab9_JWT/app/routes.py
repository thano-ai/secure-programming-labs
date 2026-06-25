# app/routes.py
from flask import render_template, request, redirect, url_for, session, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app
from app import db
from app.models import User, TokenBlocklist

from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)

# ---------- PUBLIC PAGES ----------
@app.route('/', methods=['GET'])
def login_page():
    # Render a page that posts to /api/login
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("User created! Please login.")
            return redirect(url_for('login_page'))
    return render_template('register.html')

# ---------- JWT API ----------
@app.post('/api/login')
def api_login():
    data = request.get_json(silent=True) or request.form  # allow JSON or form
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify(msg="Invalid credentials"), 401

    # Create short-lived access token and a refresh token
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(access_token=access_token, refresh_token=refresh_token)

@app.post('/api/refresh')
@jwt_required(refresh=True)
def api_refresh():
    """
    Rotate the refresh token: revoke the current one and issue a new pair.
    Client must send: Authorization: Bearer <refresh_token>
    """
    jwt_payload = get_jwt()
    jti = jwt_payload["jti"]
    db.session.add(TokenBlocklist(jti=jti, reason="refresh_rotation"))
    db.session.commit()

    user_id = get_jwt_identity()
    new_access = create_access_token(identity=user_id)
    new_refresh = create_refresh_token(identity=user_id)
    return jsonify(access_token=new_access, refresh_token=new_refresh)

@app.post('/api/logout')
@jwt_required()  # access token required to logout the current session
def api_logout():
    """
    Revoke current access token. If the client also sends a refresh token,
    call /api/logout_refresh with it to revoke that too.
    """
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti, reason="logout_access"))
    db.session.commit()
    return jsonify(msg="Access token revoked")

@app.post('/api/logout_refresh')
@jwt_required(refresh=True)
def api_logout_refresh():
    """
    Revoke the current refresh token (e.g., logout from this device).
    """
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti, reason="logout_refresh"))
    db.session.commit()
    return jsonify(msg="Refresh token revoked")

# Example protected JSON API
@app.get('/api/dashboard')
@jwt_required()
def api_dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify(message=f"Hello, {user.username}!"), 200

# Optional: whoami for debugging
@app.get('/whoami')
@jwt_required(optional=True)
def whoami():
    user_id = get_jwt_identity()
    user = User.query.get(user_id) if user_id else None
    return jsonify(
        authenticated=bool(user_id),
        user=getattr(user, "username", None)
    )
