from datetime import datetime
from database import db

class Usuario(db.Model):
    __tablename__ = 'usuarios' 
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ Relación con roles a través de la tabla intermedia
    roles = db.relationship("Rol", secondary="roles_usuario", backref="usuarios")

    def __repr__(self):
        return f'<Usuario {self.nombre} {self.apellido}>'

class Rol(db.Model):
    __tablename__ = 'roles'
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Rol {self.nombre_rol}>'

class Permiso(db.Model):
    __tablename__ = 'permisos'
    id_permiso = db.Column(db.Integer, primary_key=True)
    nombre_permiso = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))

    def __repr__(self):
        return f'<Permiso {self.nombre_permiso}>'

class RolUsuario(db.Model):
    __tablename__ = 'roles_usuario'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), primary_key=True)

    def __repr__(self):
        return f'<RolUsuario Usuario:{self.id_usuario} Rol:{self.id_rol}>'

# Tablas de productos y jerarquía de categorías
class Categoria(db.Model):
    __tablename__ = 'categoria'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre_grupo = db.Column(db.String(30), nullable=False)

    productos = db.relationship('Producto', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<Categoria {self.nombre_grupo}>'

class Producto(db.Model):
    __tablename__ = 'productos'
    id_grupo_producto = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'), nullable=False)
    nom_producto = db.Column(db.String(30), nullable=False)
    valor_producto = db.Column(db.Integer, nullable=False)
    estado_producto = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Producto {self.nom_producto}>'
