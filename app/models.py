from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import relationship

from flask_login import UserMixin  # Esta clase nos ayuda para hacer las validaciones del usuario
from app import login_manager
from app.db import Base, session


# Con este decorador la extesion identificara el usuario por su id
@login_manager.user_loader
def obtener_usuario_actual(user_id):
    return session.query(Usuario).get(int(user_id))


class Usuario(Base, UserMixin):
    __tablename__ = 'usuario'
    __tableargs__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    nombre_usuario = Column(String(length=20), unique=True, nullable=False)
    email_usuario = Column(String(length=120), unique=True, nullable=False)
    password_usuario = Column(String(length=60), nullable=False)
    imagen_usuario = Column(String(length=20), nullable=False, default='default.jpg')

    def __init__(self, nombre_usuario, email_usuario, password_usuario, imagen_usuario='default.jpg'):
        self.nombre_usuario = nombre_usuario
        self.email_usuario = email_usuario
        self.password_usuario = password_usuario
        self.imagen_usuario = imagen_usuario


# Tabla Categoria
class Categoria(Base):
    __tablename__ = 'categoria'
    __tableargs__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    nombre_categoria = Column(String(length=15), nullable=False)
    usuario_id = Column(ForeignKey('usuario.id'), nullable=False)

    usuario = relationship('Usuario', backref='categorias')  # Accedo al usuario desde la instancia Categoria

    def __init__(self, nombre_categoria, usuario_id):
        self.nombre_categoria = nombre_categoria
        self.usuario_id = usuario_id


# Tabla Transaccion
class Transaccion(Base):
    __tablename__ = 'transaccion'
    __tableargs__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    ingreso = Column(Float, default=0.0)
    gasto = Column(Float, default=0.0)
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categoria.id'), nullable=False)
    fecha_transaccion = Column(Date, default=datetime.utcnow())

    usuario = relationship('Usuario', backref='transacciones')
    categoria = relationship('Categoria', backref='transacciones')

    def __init__(self, ingreso, gasto, usuario_id, categoria_id):
        self.ingreso = ingreso
        self.gasto = gasto
        self.usuario_id = usuario_id
        self.categoria_id = categoria_id
