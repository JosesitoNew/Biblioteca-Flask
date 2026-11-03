import re

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from ...decorators import admin_required
from ...extensions import db
from ...models import Usuario

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


def _valores(usuario=None):
    if usuario:
        return {
            "nombre": usuario.nombre,
            "username": usuario.username,
            "email": usuario.email,
            "rol": usuario.rol,
        }
    return {"nombre": "", "username": "", "email": "", "rol": "usuario"}


def _validar(usuario=None):
    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "username": request.form.get("username", "").strip().lower(),
        "email": request.form.get("email", "").strip().lower(),
        "rol": request.form.get("rol", "usuario"),
    }
    password = request.form.get("password", "")
    errores = []

    if not datos["nombre"]:
        errores.append("El nombre es obligatorio.")
    if not re.fullmatch(r"[a-zA-Z0-9_.-]{3,50}", datos["username"]):
        errores.append("El usuario debe tener 3 a 50 caracteres (letras, números, . - _).")
    if "@" not in datos["email"]:
        errores.append("Ingrese un correo electrónico válido.")
    if datos["rol"] not in ("usuario", "admin"):
        errores.append("El rol seleccionado no es válido.")
    if usuario is None or password:
        if len(password) < 6:
            errores.append("La contraseña debe tener al menos 6 caracteres.")

    consulta = Usuario.query.filter(db.func.lower(Usuario.username) == datos["username"])
    if usuario:
        consulta = consulta.filter(Usuario.id != usuario.id)
    if consulta.first():
        errores.append("El nombre de usuario ya está registrado.")

    consulta = Usuario.query.filter(db.func.lower(Usuario.email) == datos["email"])
    if usuario:
        consulta = consulta.filter(Usuario.id != usuario.id)
    if consulta.first():
        errores.append("El correo electrónico ya está registrado.")

    return datos, password, errores


@usuarios_bp.route("/")
@admin_required
def lista():
    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    return render_template("usuarios/lista.html", usuarios=usuarios)


@usuarios_bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo():
    if request.method == "POST":
        datos, password, errores = _validar()
        if not errores:
            usuario = Usuario(**datos)
            usuario.set_password(password)
            db.session.add(usuario)
            db.session.commit()
            flash("Usuario registrado correctamente.", "success")
            return redirect(url_for("usuarios.lista"))
        for error in errores:
            flash(error, "danger")
        return render_template("usuarios/formulario.html", usuario=None, valores=datos)

    return render_template("usuarios/formulario.html", usuario=None, valores=_valores())


@usuarios_bp.route("/<int:usuario_id>/editar", methods=["GET", "POST"])
@admin_required
def editar(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)

    if request.method == "POST":
        datos, password, errores = _validar(usuario)
        if not errores:
            usuario.nombre = datos["nombre"]
            usuario.username = datos["username"]
            usuario.email = datos["email"]
            usuario.rol = datos["rol"]
            if password:
                usuario.set_password(password)
            db.session.commit()
            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for("usuarios.lista"))
        for error in errores:
            flash(error, "danger")
        return render_template("usuarios/formulario.html", usuario=usuario, valores=datos)

    return render_template("usuarios/formulario.html", usuario=usuario, valores=_valores(usuario))


@usuarios_bp.route("/<int:usuario_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)

    if usuario.id == current_user.id:
        flash("No puede eliminar su propio usuario.", "warning")
    elif usuario.libros:
        flash("No se puede eliminar: el usuario tiene libros registrados.", "warning")
    else:
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuario eliminado correctamente.", "success")

    return redirect(url_for("usuarios.lista"))
