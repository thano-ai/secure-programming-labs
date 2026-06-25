from app import db
from flask_login import UserMixin
from app import login_manager
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    active_session_token = db.Column(db.String(128), unique=True, nullable=True)
    active_session_expiry = db.Column(db.DateTime, nullable=True)

    def is_session_active(self):
        """Return True if user has an active (non-expired) server-side session."""
        if not self.active_session_token:
            return False
        if not self.active_session_expiry:
            return True
        return self.active_session_expiry > datetime.utcnow()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
