from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "database.db"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nume_utilizator = db.Column(db.String(8), unique=True)
    parola = db.Column(db.String(30))
    cnp = db.Column(db.String(13), unique=True)
    serie = db.Column(db.String(8))
    nume = db.Column(db.String(30))
    prenume = db.Column(db.String(30))
    loc_nastere = db.Column(db.String(150))
    domiciliu = db.Column(db.String(150))
    emis_expirare = db.Column(db.String(150))
