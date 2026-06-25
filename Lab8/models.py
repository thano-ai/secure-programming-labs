from flask_sqlalchemy import SQLAlchemy
from flask_argon2 import Argon2
from flask_login import UserMixin

db = SQLAlchemy()
argon2 = Argon2()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    ssn_encrypted = db.Column(db.LargeBinary, nullable=True)

    def set_password(self, password):
        self.password_hash = argon2.generate_password_hash(password)

    def check_password(self, password):
        return argon2.check_password_hash(self.password_hash, password)

