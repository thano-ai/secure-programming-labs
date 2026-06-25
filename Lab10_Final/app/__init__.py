from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secrets
import logging
from logging.handlers import RotatingFileHandler
import os


db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secrets.token_hex(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"

    # ===== Logging Setup =====
    if not os.path.exists("logs"):
        os.mkdir("logs")

    file_handler = RotatingFileHandler("logs/app.log", maxBytes=10240, backupCount=3)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] in %(module)s: %(message)s"
    ))
    file_handler.setLevel(logging.ERROR)

    # Attach handler to app.logger and werkzeug
    app.logger.addHandler(file_handler)
    logging.getLogger("werkzeug").addHandler(file_handler)

    # Make sure log level is set
    app.logger.setLevel(logging.ERROR)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    # --- Init extensions ---
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import routes
        db.create_all()

    return app
