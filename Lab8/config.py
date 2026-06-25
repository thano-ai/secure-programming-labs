import os
from cryptography.fernet import Fernet

class Config:
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    # ENCRYPTION_KEY = Fernet.generate_key()
    ENCRYPTION_KEY = 'LPEQwivvZnDgxZQXAWCA-gN8UPOcoiApVs2grQ4t9UM='


    # generating code:


