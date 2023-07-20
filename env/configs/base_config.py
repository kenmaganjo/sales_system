import secrets
import os


class Base:
    Flask_APP = "main.py"
    SECRET_KEY = secrets.token_hex(16)

class Development(Base):
    FLASK_ENV = 'development'
    DATABASE = 'myduka'
    POSTGRES_USER = 'progres'
    POSTGRES_PASSWORD = os.environ.get("1958")