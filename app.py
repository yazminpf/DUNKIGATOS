from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from models import Usuario, Rol, Permiso, RolUsuario, Categoria, Producto, Factura, DetalleFactura
from database import db
import os
from functools import wraps
from flask import jsonify 

app = Flask(__name__)

import secrets
app.secret_key = secrets.token_hex(16)

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

# Decorador para restringir acceso solo a administradores
def solo_admins(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))

        usuario = Usuario.query.get(session["usuario_id"])
        if not usuario or not any(rol.nombre_rol == "administrador" for rol in usuario.roles):
            return abort(403)

        return f(*args, **kwargs)
    return decorada

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
            session["usuario_id"] = usuario.id_usuario
            session["nombre_usuario"] = f"{usuario.nombre} {usuario.apellido}"

            if any(rol.nombre_rol == "administrador" for rol in usuario.roles):
                return redirect(url_for("panel_admin"))
            else:
                return redirect(url_for("ver_categorias"))
        else:
            return render_template("login.html", mensaje="❌ Credenciales incorrectas")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Página de registro de usuario
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        correo = request.form["correo"]
        password = request.form["password"]
        confirmar = request.form["confirmar"]

        if password != confirmar:
            return render_template("registro.html", mensaje="❌ Las contraseñas no coinciden")

        usuario_existente = Usuario.query.filter_by(correo=correo).first()
        if usuario_existente:
            return render_template("registro.html", mensaje="❌ El correo ya está registrado")

        nuevo_usuario = Usuario(nombre=nombre, apellido=apellido, correo=correo, password=password)
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

@app.route("/admin/usuarios")
@solo_admins
def admin_usuarios():
    usuarios = Usuario.query.all()
    roles = Rol.query.all()
    return render_template("usuarios_admin.html", usuarios=usuarios, roles=roles)

@app.route("/admin/asignar_rol/<int:usuario_id>", methods=["POST"])
def asignar_rol(usuario_id):
    nuevo_rol_id = request.form.get("rol_id")
    rol_existente = RolUsuario.query.filter_by(id_usuario=usuario_id).first()
    if rol_existente:
        rol_existente.id_rol = nuevo_rol_id
    else:
        nuevo_rol = RolUsuario(id_usuario=usuario_id, id_rol=nuevo_rol_id)
        db.session.add(nuevo_rol)
    db.session.commit()
    return redirect(url_for("admin_usuarios"))

@app.route("/admin/panel")
@solo_admins
def panel_admin():
    return render_template("panel_admin.html")

@app.route("/admin/permisos", methods=["GET", "POST"])
@solo_admins
def admin_permisos():
    mensaje = None
    if request.method == "POST":
        nombre = request.form["nombre_permiso"]
        descripcion = request.form["descripcion"]

        if Permiso.query.filter_by(nombre_permiso=nombre).first():
            mensaje = "❌ El permiso ya existe"
        else:
            db.session.add(Permiso(nombre_permiso=nombre, descripcion=descripcion))
            db.session.commit()
            mensaje = "✅ Permiso creado correctamente"

    permisos = Permiso.query.all()
    roles = Rol.query.all()
    return render_template("permisos_admin.html", permisos=permisos, roles=roles, mensaje=mensaje)

@app.route("/admin/asignar_permiso", methods=["POST"])
@solo_admins
def asignar_permiso_a_rol():
    id_rol = request.form.get("id_rol")
    id_permiso = request.form.get("id_permiso")

    from models import RolPermiso
    existe = RolPermiso.query.filter_by(id_rol=id_rol, id_permiso=id_permiso).first()
    if not existe:
        nuevo = RolPermiso(id_rol=id_rol, id_permiso=id_permiso)
        db.session.add(nuevo)
        db.session.commit()

    return redirect(url_for("admin_permisos"))

@app.route("/admin/productos")
@solo_admins
def admin_productos():
    productos = Producto.query.all()
    categorias = Categoria.query.all()
    return render_template("admin_productos.html", productos=productos, categorias=categorias)

@app.route("/admin/productos/crear", methods=["GET", "POST"])
@solo_admins
def crear_producto():
    if request.method == "POST":
        nom_producto = request.form["nom_producto"]
        valor_producto = int(request.form["valor_producto"])
        id_categoria = int(request.form["id_categoria"])

        print("💾 Creando producto:", nom_producto, valor_producto, id_categoria)

        nuevo = Producto(
            nom_producto=nom_producto,
            valor_producto=valor_producto,
            id_categoria=id_categoria,
            estado_producto=True
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("admin_productos"))

    categorias = Categoria.query.all()
    return render_template("crear_producto.html", categorias=categorias)

@app.route("/admin/productos/editar/<int:id_producto>", methods=["GET", "POST"])
@solo_admins
def editar_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    categorias = Categoria.query.all()

    if request.method == "POST":
        producto.nom_producto = request.form["nom_producto"]
        producto.valor_producto = request.form["valor_producto"]
        producto.id_categoria = request.form["id_categoria"]

        db.session.commit()
        return redirect(url_for("admin_productos"))

    return render_template("editar_producto.html", producto=producto, categorias=categorias)

@app.route("/facturar", methods=["GET", "POST"])
def facturar():
    if request.method == "GET":
        productos = Producto.query.filter_by(estado_producto=True).all()
        return render_template("facturacion.html", productos=productos)

    if request.method == "POST":
        data = request.get_json()
        productos = data.get("productos", [])
        total = data.get("total", 0)

        if not productos or total <= 0:
            return jsonify({"mensaje": "❌ Datos inválidos"}), 400

        # Usa el usuario actual si ha iniciado sesión, o None si no
        id_usuario = session.get("usuario_id")

        factura = Factura(total=total, id_usuario=id_usuario)
        db.session.add(factura)
        db.session.commit()

        for item in productos:
            detalle = DetalleFactura(
                id_factura=factura.id_factura,
                id_producto=item["id_grupo_producto"],  # 👈 este es el cambio
                cantidad=item["cantidad"],
                subtotal=item["subtotal"]
            )
            db.session.add(detalle)


        db.session.commit()

        return jsonify({"mensaje": "✅ Factura registrada correctamente", "id_factura": factura.id_factura}), 200

# Ruta temporal para crear tablas en producción
#@app.route("/crear_tablas")
#def crear_tablas():
    #try:
       # with app.app_context():
            #db.create_all()
        #return "✅ Tablas creadas correctamente en la base de datos"
    #except Exception as e:
        #return f"❌ Error al crear las tablas: {str(e)}"

# Ejecutar app
if __name__ == "__main__":
    with app.app_context():
        probar_conexion()
        # db.create_all()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
