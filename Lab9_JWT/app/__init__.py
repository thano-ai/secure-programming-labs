# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta
from flask_jwt_extended import JWTManager
import secrets

db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secrets.token_hex(23)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    # --- Sessions no longer used for auth. Keep if you still need server sessions elsewhere. ---
    # app.config['SESSION_TYPE'] = 'filesystem'
    # app.config['SESSION_COOKIE_HTTPONLY'] = True
    # app.config['SESSION_COOKIE_SECURE'] = False  # True in production over HTTPS
    # app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # app.config['SESSION_REFRESH_EACH_REQUEST'] = True

    # ---------------- JWT CONFIG ----------------
    app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)  # separate secret for JWT
    app.config['JWT_TOKEN_LOCATION'] = ['headers']        # tokens via Authorization: Bearer <token>
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)

    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from . import routes  # imports endpoints below
        db.create_all()

    return app
