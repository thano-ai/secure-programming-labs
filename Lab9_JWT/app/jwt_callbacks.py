# app/jwt_callbacks.py
from flask import request
from app import db, jwt
from app.models import TokenBlocklist
from flask_jwt_extended import get_jwt

@jwt.token_in_blocklist_loader
def is_token_revoked(jwt_header, jwt_payload):
    # Deny tokens whose JTI is in blocklist
    jti = jwt_payload["jti"]
    return db.session.query(TokenBlocklist.id).filter_by(jti=jti).first() is not None
