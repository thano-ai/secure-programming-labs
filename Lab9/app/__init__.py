from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
import secrets
from datetime import timedelta

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secrets.token_hex(23)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    ### Comment: for session Hijacking
    app.config['SESSION_TYPE'] = 'filesystem'

    ### Comment: for session Hijacking
    # Secure session cookies
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # True in production over HTTPS
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)

    ### Uncomment : for session Hijacking
    # Insecure session cookies (vulnerable setup)
    # app.config['SESSION_COOKIE_HTTPONLY'] = False   # allow JavaScript to read cookie
    # app.config['SESSION_COOKIE_SECURE'] = False     # send cookie over HTTP
    # app.config['SESSION_COOKIE_SAMESITE'] = None    # allow cross-site requests
    # app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 1 day, long-lived
    # app.config['SESSION_REFRESH_EACH_REQUEST'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.session_protection = "strong"
    ### Uncomment: for session Hijacking
    # login_manager.session_protection = None
    ### Comment: for session Hijacking
    Session(app)

    with app.app_context():
        from . import routes
        db.create_all()

    return app



