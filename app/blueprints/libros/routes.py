from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from ...decorators import propietario_o_admin
from ...extensions import db
from ...models import Categoria, Libro

libros_bp = Blueprint("libros", __name__, url_prefix="/libros")


def _valores(libro=None):
    if libro:
        return {
            "titulo": libro.titulo,
            "autor": libro.autor,
            "anio": libro.anio,
            "descripcion": libro.descripcion or "",
            "categoria_id": libro.categoria_id,
            "disponible": libro.disponible,
        }
    return {
        "titulo": "",
        "autor": "",
        "anio": "",
        "descripcion": "",
        "categoria_id": None,
        "disponible": True,
    }


def _validar():
    datos = {
        "titulo": request.form.get("titulo", "").strip(),
        "autor": request.form.get("autor", "").strip(),
        "anio": request.form.get("anio", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip(),
        "categoria_id": request.form.get("categoria_id", type=int),
        "disponible": request.form.get("disponible") == "on",
    }
    errores = []

    if not datos["titulo"]:
        errores.append("El título es obligatorio.")
    if not datos["autor"]:
        errores.append("El autor es obligatorio.")

    anio_actual = datetime.now().year
    if not datos["anio"].isdigit() or not (1000 <= int(datos["anio"]) <= anio_actual):
        errores.append(f"El año debe estar entre 1000 y {anio_actual}.")
    else:
        datos["anio"] = int(datos["anio"])

    if not datos["categoria_id"] or not db.session.get(Categoria, datos["categoria_id"]):
        errores.append("Seleccione una categoría válida.")

    return datos, errores


@libros_bp.route("/")
@login_required
def lista():
    busqueda = request.args.get("q", "").strip()
    categoria_id = request.args.get("categoria", type=int)

    consulta = Libro.query
    if categoria_id:
        consulta = consulta.filter_by(categoria_id=categoria_id)
    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(or_(Libro.titulo.ilike(patron), Libro.autor.ilike(patron)))

    libros = consulta.order_by(Libro.titulo).all()
    categorias = Categoria.query.order_by(Categoria.nombre).all()

    return render_template(
        "libros/lista.html",
        libros=libros,
        categorias=categorias,
        busqueda=busqueda,
        categoria_id=categoria_id,
    )


@libros_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    categorias = Categoria.query.order_by(Categoria.nombre).all()

    if request.method == "POST":
        datos, errores = _validar()
        if not errores:
            libro = Libro(**datos, usuario_id=current_user.id)
            db.session.add(libro)
            db.session.commit()
            flash("Libro registrado correctamente.", "success")
            return redirect(url_for("libros.lista"))
        for error in errores:
            flash(error, "danger")
        return render_template("libros/formulario.html", libro=None, valores=datos, categorias=categorias)

    return render_template("libros/formulario.html", libro=None, valores=_valores(), categorias=categorias)


@libros_bp.route("/<int:libro_id>/editar", methods=["GET", "POST"])
@login_required
def editar(libro_id):
    libro = db.get_or_404(Libro, libro_id)
    if not propietario_o_admin(libro):
        abort(403)

    categorias = Categoria.query.order_by(Categoria.nombre).all()

    if request.method == "POST":
        datos, errores = _validar()
        if not errores:
            for campo, valor in datos.items():
                setattr(libro, campo, valor)
            db.session.commit()
            flash("Libro actualizado correctamente.", "success")
            return redirect(url_for("libros.lista"))
        for error in errores:
            flash(error, "danger")
        return render_template("libros/formulario.html", libro=libro, valores=datos, categorias=categorias)

    return render_template("libros/formulario.html", libro=libro, valores=_valores(libro), categorias=categorias)


@libros_bp.route("/<int:libro_id>/eliminar", methods=["POST"])
@login_required
def eliminar(libro_id):
    libro = db.get_or_404(Libro, libro_id)
    if not propietario_o_admin(libro):
        abort(403)

    db.session.delete(libro)
    db.session.commit()
    flash("Libro eliminado correctamente.", "success")
    return redirect(url_for("libros.lista"))
