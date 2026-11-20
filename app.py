"""MotoControl Ubaté - aplicación web (Flask + MySQL).

Cada ruta (@app.route) es un módulo o pantalla del sistema. Las pantallas se
dibujan con la plantilla templates/modulo.html a partir de los datos que arma
la función pagina().
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from mysql.connector import Error, IntegrityError

from db import BaseDatos
from modelos import (Cliente, Motocicleta, Repuesto,
                     OrdenServicio, Recordatorio)
from tad import ColaFIFO

# Instancia de la aplicación. La clave secreta es necesaria para los mensajes flash.
app = Flask(__name__)
app.secret_key = "cambie-esta-clave-secreta"
# Objeto único de acceso a la base de datos (ver db.py).
bd = BaseDatos()

# Lista fija de consejos que se muestran en el módulo "Consejos".
CONSEJOS = [
    "Revise periódicamente el nivel y estado del aceite.",
    "Verifique la presión y el desgaste de las llantas.",
    "Revise frenos, luces y direccionales.",
    "Mantenga la cadena limpia, lubricada y ajustada.",
    "Realice los mantenimientos según el fabricante.",
    "Registre el kilometraje después de cada servicio.",
    "Estos consejos no reemplazan la revisión de un mecánico.",
]


# ---------- utilidades ----------
# Si MySQL falla (apagado, tabla inexistente...), se muestra un mensaje claro
# en pantalla en lugar de una página de error genérica.
@app.errorhandler(Error)
def error_bd(e):
    return pagina("Error de base de datos", lista=[
        "Verifique que MySQL esté iniciado en XAMPP y que ejecutó init_db.py.",
        str(e)]), 500


# Describe un campo de formulario: nombre, etiqueta, tipo y (opcional) lista desplegable.
def campo(n, l, t="text", opciones=None, step=None):
    return dict(n=n, l=l, t=t, opciones=opciones, step=step)


# Renderiza cualquier módulo con la plantilla genérica modulo.html
# (título, tabla de datos, formularios y/o lista de textos).
def pagina(titulo, columnas=None, filas=(), formularios=(), lista=None):
    return render_template("modulo.html", titulo=titulo, columnas=columnas,
                           filas=filas, formularios=formularios, lista=lista)


# Valida una entidad (POO) y la guarda en la base de datos.
# Devuelve True si se guardó; si no, muestra el error con flash().
def registrar(entidad):
    error = entidad.validar()
    if error:
        flash(error, "error")
        return False
    try:
        bd.insertar(entidad)
    except IntegrityError:
        flash("No se pudo guardar: dato repetido (ej. placa) o referencia inválida.", "error")
        return False
    flash("Registro guardado correctamente.", "ok")
    return True


# Lista (id, texto) de motocicletas para llenar los menús desplegables.
def opciones_motos():
    return [(m["id"], f"{m['placa']} - {m['marca']} {m['modelo']}")
            for m in bd.consultar("SELECT id, placa, marca, modelo FROM motocicletas ORDER BY id")]


# Construye el TAD Cola FIFO con las órdenes en estado "Pendiente",
# ordenadas por id (la más antigua queda al frente).
def cargar_cola():
    cola = ColaFIFO()
    for o in bd.consultar(
            "SELECT o.id, m.placa, o.descripcion, o.fecha, o.mecanico FROM ordenes o "
            "JOIN motocicletas m ON m.id = o.id_moto "
            "WHERE o.estado = 'Pendiente' ORDER BY o.id"):
        cola.encolar(o)
    return cola


# ---------- inicio ----------
@app.route("/")
def inicio():
    return pagina("Inicio", lista=[
        "Bienvenido(a) a MotoControl Ubaté.",
        "Use el menú superior para navegar por los módulos disponibles."])


# ---------- clientes y motos ----------
# GET: muestra clientes y formulario. POST: registra un cliente nuevo.
@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    if request.method == "POST":
        registrar(Cliente(**request.form.to_dict()))
        return redirect(url_for("clientes"))
    form = dict(titulo="Registrar cliente", accion=url_for("clientes"), campos=[
        campo("nombre", "Nombre completo"), campo("telefono", "Teléfono"),
        campo("correo", "Correo", "email")])
    return pagina("Clientes",
                  [("id", "ID"), ("nombre", "Nombre"), ("telefono", "Teléfono"), ("correo", "Correo")],
                  bd.consultar("SELECT * FROM clientes ORDER BY id"), [form])


# GET: lista motocicletas y su propietario. POST: registra una moto (placa única).
@app.route("/motos", methods=["GET", "POST"])
def motos():
    if request.method == "POST":
        registrar(Motocicleta(**request.form.to_dict()))
        return redirect(url_for("motos"))
    ops = [(c["id"], f"{c['id']} - {c['nombre']}")
           for c in bd.consultar("SELECT id, nombre FROM clientes ORDER BY id")]
    form = dict(titulo="Registrar motocicleta", accion=url_for("motos"), campos=[
        campo("id_cliente", "Propietario", opciones=ops), campo("placa", "Placa"),
        campo("marca", "Marca"), campo("modelo", "Modelo"),
        campo("kilometraje", "Kilometraje actual", "number")])
    filas = bd.consultar(
        "SELECT m.*, c.nombre AS propietario FROM motocicletas m "
        "JOIN clientes c ON c.id = m.id_cliente ORDER BY m.id")
    return pagina("Motocicletas",
                  [("id", "ID"), ("placa", "Placa"), ("marca", "Marca"), ("modelo", "Modelo"),
                   ("kilometraje", "Km"), ("propietario", "Propietario")], filas, [form])


# ---------- órdenes de servicio ----------
# GET: lista órdenes y formularios. POST: crea una orden (estado inicial "Pendiente").
@app.route("/ordenes", methods=["GET", "POST"])
def ordenes():
    if request.method == "POST":
        registrar(OrdenServicio(**request.form.to_dict()))
        return redirect(url_for("ordenes"))
    abiertas = [(o["id"], f"#{o['id']} - {o['placa']} - {o['descripcion']}") for o in bd.consultar(
        "SELECT o.id, m.placa, o.descripcion FROM ordenes o "
        "JOIN motocicletas m ON m.id = o.id_moto WHERE o.estado <> 'Finalizada' ORDER BY o.id")]
    formularios = [
        dict(titulo="Crear orden", accion=url_for("ordenes"), campos=[
            campo("id_moto", "Motocicleta", opciones=opciones_motos()),
            campo("descripcion", "Servicio solicitado"), campo("fecha", "Fecha de ingreso", "date"),
            campo("mecanico", "Mecánico responsable")]),
        dict(titulo="Atender siguiente orden (FIFO)", accion=url_for("atender"),
             boton="Atender siguiente", campos=[]),
        dict(titulo="Registrar trabajo realizado", accion=url_for("trabajo"), campos=[
            campo("id_orden", "Orden", opciones=abiertas), campo("descripcion", "Trabajo realizado"),
            campo("fecha", "Fecha del trabajo", "date"), campo("kilometraje", "Kilometraje", "number")]),
    ]
    filas = bd.consultar(
        "SELECT o.*, m.placa FROM ordenes o JOIN motocicletas m ON m.id = o.id_moto ORDER BY o.id")
    return pagina("Órdenes de servicio",
                  [("id", "Orden"), ("placa", "Placa"), ("fecha", "Fecha"), ("estado", "Estado"),
                   ("mecanico", "Mecánico"), ("descripcion", "Trabajo")], filas, formularios)


# Saca la orden más antigua de la cola FIFO y la pasa a "En proceso".
@app.route("/ordenes/atender", methods=["POST"])
def atender():
    orden = cargar_cola().desencolar()
    if orden is None:
        flash("No hay órdenes pendientes.", "error")
    else:
        bd.ejecutar("UPDATE ordenes SET estado='En proceso' WHERE id=%s", (orden["id"],))
        flash(f"Orden #{orden['id']} ({orden['placa']}) pasó a estado: En proceso.", "ok")
    return redirect(url_for("ordenes"))


# Guarda el trabajo realizado, finaliza la orden y actualiza el kilometraje de la moto.
@app.route("/ordenes/trabajo", methods=["POST"])
def trabajo():
    f = request.form
    if not f.get("kilometraje", "").isdigit() or not f.get("id_orden"):
        flash("Datos inválidos: revise la orden y el kilometraje.", "error")
        return redirect(url_for("ordenes"))
    km = int(f["kilometraje"])
    bd.ejecutar("INSERT INTO trabajos (id_orden, descripcion, fecha, kilometraje) VALUES (%s,%s,%s,%s)",
                (f["id_orden"], f["descripcion"], f["fecha"], km))
    bd.ejecutar("UPDATE ordenes SET estado='Finalizada' WHERE id=%s", (f["id_orden"],))
    bd.ejecutar("UPDATE motocicletas m JOIN ordenes o ON o.id_moto = m.id "
                "SET m.kilometraje=%s WHERE o.id=%s", (km, f["id_orden"]))
    flash("Trabajo guardado en el historial. Orden finalizada.", "ok")
    return redirect(url_for("ordenes"))


# Muestra las órdenes pendientes en el orden en que serán atendidas.
@app.route("/cola")
def cola():
    filas = [dict(o, posicion=i) for i, o in enumerate(cargar_cola().elementos(), 1)]
    return pagina("Cola de órdenes pendientes (FIFO)",
                  [("posicion", "Posición"), ("id", "Orden"), ("placa", "Placa"),
                   ("descripcion", "Trabajo"), ("fecha", "Fecha"), ("mecanico", "Mecánico")], filas,
                  lista=["FIFO: primero en entrar, primero en ser atendido."])


# ---------- repuestos ----------
# GET: inventario y formularios. POST: registra un repuesto nuevo.
@app.route("/repuestos", methods=["GET", "POST"])
def repuestos():
    if request.method == "POST":
        registrar(Repuesto(**request.form.to_dict()))
        return redirect(url_for("repuestos"))
    ops = [(r["id"], f"{r['id']} - {r['nombre']}") for r in bd.consultar("SELECT id, nombre FROM repuestos")]
    formularios = [
        dict(titulo="Registrar repuesto", accion=url_for("repuestos"), campos=[
            campo("nombre", "Nombre"), campo("cantidad", "Cantidad inicial", "number"),
            campo("precio", "Precio por unidad", "number", step="0.01")]),
        dict(titulo="Registrar entrada de unidades", accion=url_for("entrada"), campos=[
            campo("id", "Repuesto", opciones=ops), campo("unidades", "Unidades que ingresan", "number")]),
    ]
    return pagina("Control de repuestos",
                  [("id", "ID"), ("nombre", "Nombre"), ("cantidad", "Cantidad"), ("precio", "Precio ($)")],
                  bd.consultar("SELECT * FROM repuestos ORDER BY id"), formularios)


# Suma unidades al inventario de un repuesto (la cantidad debe ser mayor que 0).
@app.route("/repuestos/entrada", methods=["POST"])
def entrada():
    u = request.form.get("unidades", "")
    if not u.isdigit() or int(u) <= 0:
        flash("Debe ingresar una cantidad mayor que cero.", "error")
    else:
        bd.ejecutar("UPDATE repuestos SET cantidad = cantidad + %s WHERE id=%s",
                    (int(u), request.form.get("id")))
        flash("Inventario actualizado.", "ok")
    return redirect(url_for("repuestos"))


# ---------- historial, recordatorios, consejos ----------
# Historial de trabajos realizados; se puede filtrar por motocicleta (?moto=id).
@app.route("/historial")
def historial():
    moto = request.args.get("moto")
    sql = ("SELECT t.fecha, t.descripcion, t.kilometraje, o.id AS orden, m.placa FROM trabajos t "
           "JOIN ordenes o ON o.id = t.id_orden JOIN motocicletas m ON m.id = o.id_moto")
    filas = bd.consultar(sql + (" WHERE m.id=%s" if moto else "") + " ORDER BY t.fecha DESC",
                         (moto,) if moto else ())
    form = dict(titulo="Filtrar por motocicleta", accion=url_for("historial"), metodo="get",
                boton="Consultar", campos=[campo("moto", "Motocicleta", opciones=opciones_motos())])
    return pagina("Historial de mantenimiento",
                  [("placa", "Placa"), ("orden", "Orden"), ("fecha", "Fecha"),
                   ("descripcion", "Trabajo"), ("kilometraje", "Km")], filas, [form])


# GET: lista recordatorios. POST: crea uno (el km objetivo no puede ser menor al actual).
@app.route("/recordatorios", methods=["GET", "POST"])
def recordatorios():
    if request.method == "POST":
        f = request.form.to_dict()
        m = bd.uno("SELECT kilometraje FROM motocicletas WHERE id=%s", (f.get("id_moto"),))
        if m and f.get("km_objetivo", "").isdigit() and int(f["km_objetivo"]) >= m["kilometraje"]:
            registrar(Recordatorio(**f))
        else:
            flash("El kilometraje objetivo no puede ser menor al actual.", "error")
        return redirect(url_for("recordatorios"))
    form = dict(titulo="Crear recordatorio", accion=url_for("recordatorios"), campos=[
        campo("id_moto", "Motocicleta", opciones=opciones_motos()),
        campo("descripcion", "Mantenimiento a realizar"), campo("fecha", "Fecha recomendada", "date"),
        campo("km_objetivo", "Kilometraje recomendado", "number")])
    filas = bd.consultar("SELECT r.*, m.placa FROM recordatorios r "
                         "JOIN motocicletas m ON m.id = r.id_moto ORDER BY r.fecha")
    return pagina("Recordatorios de mantenimiento",
                  [("placa", "Placa"), ("descripcion", "Mantenimiento"), ("fecha", "Fecha"),
                   ("km_objetivo", "Km objetivo")], filas, [form])


# Consejos de mantenimiento preventivo (lista estática).
@app.route("/consejos")
def consejos():
    return pagina("Consejos de mantenimiento preventivo", lista=CONSEJOS)


# Arranque del servidor de desarrollo: http://127.0.0.1:5000
if __name__ == "__main__":
    app.run(debug=True)
