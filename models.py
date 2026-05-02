from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Usuario(UserMixin, db.Model):

    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())

    proyectos = db.relationship(
        "Proyecto",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Usuario {self.username}>"


class Proyecto(db.Model):

    __tablename__ = "proyectos"

    id = db.Column(db.Integer, primary_key=True)

    inversion = db.Column(db.Float, nullable=False)

    tasa = db.Column(db.Float, nullable=False)

    vpn = db.Column(db.Float)

    tir = db.Column(db.Float)

    analisis = db.Column(db.String(300))

    fecha = db.Column(db.DateTime, server_default=db.func.now())

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Proyecto VPN={self.vpn} TIR={self.tir}>"