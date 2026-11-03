from flask import Blueprint, render_template

from ...models import Categoria, Libro, Usuario

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    libros_recientes = Libro.query.order_by(Libro.fecha_registro.desc()).limit(6).all()
    estadisticas = {
        "libros": Libro.query.count(),
        "categorias": Categoria.query.count(),
        "usuarios": Usuario.query.count(),
    }
    return render_template(
        "main/index.html",
        libros_recientes=libros_recientes,
        estadisticas=estadisticas,
    )
