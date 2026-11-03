from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ...models import Usuario

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _destino_seguro(destino):
    if destino and destino.startswith("/") and not destino.startswith("//"):
        return destino
    return url_for("main.index")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        recordar = request.form.get("remember") == "on"

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and usuario.check_password(password):
            login_user(usuario, remember=recordar)
            flash(f"Bienvenido, {usuario.nombre}.", "success")
            return redirect(_destino_seguro(request.args.get("next")))

        flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión finalizada correctamente.", "info")
    return redirect(url_for("auth.login"))
