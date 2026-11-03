from flask import Blueprint, flash, redirect, render_template, request, url_for

from ...decorators import admin_required
from ...extensions import db
from ...models import Categoria

categorias_bp = Blueprint("categorias", __name__, url_prefix="/categorias")


def _validar(categoria=None):
    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip(),
    }
    errores = []

    if not datos["nombre"]:
        errores.append("El nombre de la categoría es obligatorio.")

    if datos["nombre"]:
        consulta = Categoria.query.filter(
            db.func.lower(Categoria.nombre) == datos["nombre"].lower()
        )
        if categoria:
            consulta = consulta.filter(Categoria.id != categoria.id)
        if consulta.first():
            errores.append("Ya existe una categoría con ese nombre.")

    return datos, errores


@categorias_bp.route("/")
@admin_required
def lista():
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return render_template("categorias/lista.html", categorias=categorias)


@categorias_bp.route("/nueva", methods=["GET", "POST"])
@admin_required
def nueva():
    if request.method == "POST":
        datos, errores = _validar()
        if not errores:
            db.session.add(Categoria(**datos))
            db.session.commit()
            flash("Categoría registrada correctamente.", "success")
            return redirect(url_for("categorias.lista"))
        for error in errores:
            flash(error, "danger")
        return render_template("categorias/formulario.html", categoria=None, valores=datos)

    return render_template(
        "categorias/formulario.html",
        categoria=None,
        valores={"nombre": "", "descripcion": ""},
    )


@categorias_bp.route("/<int:categoria_id>/editar", methods=["GET", "POST"])
@admin_required
def editar(categoria_id):
    categoria = db.get_or_404(Categoria, categoria_id)

    if request.method == "POST":
        datos, errores = _validar(categoria)
        if not errores:
            categoria.nombre = datos["nombre"]
            categoria.descripcion = datos["descripcion"]
            db.session.commit()
            flash("Categoría actualizada correctamente.", "success")
            return redirect(url_for("categorias.lista"))
        for error in errores:
            flash(error, "danger")
        return render_template("categorias/formulario.html", categoria=categoria, valores=datos)

    return render_template(
        "categorias/formulario.html",
        categoria=categoria,
        valores={"nombre": categoria.nombre, "descripcion": categoria.descripcion or ""},
    )


@categorias_bp.route("/<int:categoria_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(categoria_id):
    categoria = db.get_or_404(Categoria, categoria_id)

    if categoria.libros:
        flash("No se puede eliminar: la categoría tiene libros asociados.", "warning")
    else:
        db.session.delete(categoria)
        db.session.commit()
        flash("Categoría eliminada correctamente.", "success")

    return redirect(url_for("categorias.lista"))
