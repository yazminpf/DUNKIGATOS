from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from models import Usuario, Rol, Permiso, RolUsuario, Categoria, Producto
from database import db
import os

app = Flask(__name__)

# Configuración de PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "postgresql://postgres:Luc1995%2B@localhost/dunki_gatos_db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos con la app
db.init_app(app)
 
# Probar conexión
def probar_conexion():
    try:
        db.session.execute(text('SELECT 1'))
        print("✅ Conexión a PostgreSQL exitosa")
    except Exception as e:
        print("❌ Error al conectar con PostgreSQL:", e)

# Página principal
@app.route("/")
def inicio():
    return render_template('index.html')

# Página de inicio de sesión
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(correo=correo, password=password).first()
        if usuario:
            return redirect(url_for("ver_categorias"))  # Asegúrate de tener esta ruta o cámbiala
        else:
            return render_template("login.html", mensaje="❌ Credenciales incorrectas")

    return render_template("login.html")

# Página de registro de usuario
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        correo = request.form["correo"]
        password = request.form["password"]

        usuario_existente = Usuario.query.filter_by(correo=correo).first()
        if usuario_existente:
            return render_template("registro.html", mensaje="❌ El correo ya está registrado")

        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            password=password
        )

        db.session.add(nuevo_usuario)
        db.session.commit()
        return render_template("registro.html", mensaje="✅ Usuario registrado correctamente")

    return render_template("registro.html")

@app.route("/categoria")
def ver_categorias():
    categorias = Categoria.query.all()
    return render_template("categoria.html", categorias=categorias)

@app.route("/productos/categoria/<int:id_categoria>")
def ver_productos_por_categoria(id_categoria):
    categoria = Categoria.query.get_or_404(id_categoria)
    productos = categoria.productos
    return render_template("productos.html", categoria=categoria, productos=productos)


# Ejecutar app
if __name__ == "__main__":
    with app.app_context():
        probar_conexion()
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

        








