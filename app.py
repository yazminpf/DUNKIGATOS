from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from models import Usuario, Rol, Permiso, RolUsuario, Categoria, Producto
from database import db

app = Flask(__name__)

# Configuración de PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Luc1995%2B@localhost/dunki_gatos_db'
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
            return redirect(url_for("inicio"))  # Asegúrate de tener esta ruta o cámbiala
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

# Ejecutar app
if __name__ == "__main__":
    with app.app_context():
        probar_conexion()
        db.create_all()

        from models import Categoria, Producto

        if not Categoria.query.first():
            categorias = [
                Categoria(nombre_grupo='PLATO PRINCIPAL'),
                Categoria(nombre_grupo='BEBIDAS'),
                Categoria(nombre_grupo='ACOMPAÑANTES')
            ]
            db.session.bulk_save_objects(categorias)
            db.session.commit()
            print("✅ Categorías insertadas")

        if not Producto.query.first():
            productos = [
                Producto(nom_producto='Pasta Pesto', valor_producto=25000, id_categoria=1),
                Producto(nom_producto='Hamburguesa', valor_producto=21000, id_categoria=1),
                Producto(nom_producto='Trucha al Ajillo', valor_producto=34000, id_categoria=1),
                Producto(nom_producto='Limonada de Coco', valor_producto=6000, id_categoria=2),
                Producto(nom_producto='Limonada Natural', valor_producto=4500, id_categoria=2),
                Producto(nom_producto='Coca cola', valor_producto=5000, id_categoria=2),
                Producto(nom_producto='Papas francesas', valor_producto=8000, id_categoria=3),
                Producto(nom_producto='Patacon', valor_producto=10000, id_categoria=3),
                Producto(nom_producto='Chorizo', valor_producto=4500, id_categoria=3),
            ]
            db.session.bulk_save_objects(productos) 
            db.session.commit()
            print("✅ Productos insertados")
    
app.run(debug=True)






