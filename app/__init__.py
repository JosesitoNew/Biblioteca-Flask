import os
from datetime import datetime

import click
from flask import Flask, render_template

from config import Config
from .extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Debes iniciar sesión para acceder a esta sección."
    login_manager.login_message_category = "warning"

    from .blueprints.auth import auth_bp
    from .blueprints.categorias import categorias_bp
    from .blueprints.libros import libros_bp
    from .blueprints.main import main_bp
    from .blueprints.usuarios import usuarios_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(libros_bp)

    from .models import Categoria, Libro, Usuario

    @login_manager.user_loader
    def cargar_usuario(usuario_id):
        return db.session.get(Usuario, int(usuario_id))

    @app.context_processor
    def variables_globales():
        return {
            "anio_actual": datetime.now().year,
            "nombre_sitio": app.config["NOMBRE_SITIO"],
            "nombre_institucion": app.config["NOMBRE_INSTITUCION"],
        }

    @app.errorhandler(403)
    def error_403(error):
        return render_template("errores/403.html"), 403

    @app.errorhandler(404)
    def error_404(error):
        return render_template("errores/404.html"), 404

    @app.cli.command("init-db")
    def init_db():
        db.create_all()

        if not Usuario.query.filter_by(username="admin").first():
            admin = Usuario(
                nombre="Administrador",
                username="admin",
                email="admin@biblioteca.com",
                rol="admin",
            )
            admin.set_password("admin123")
            db.session.add(admin)

        if Categoria.query.count() == 0:
            db.session.add_all(
                [
                    Categoria(nombre="Ficción", descripcion="Novelas y cuentos."),
                    Categoria(nombre="Ciencia", descripcion="Libros de divulgación científica."),
                    Categoria(nombre="Historia", descripcion="Hechos y procesos históricos."),
                    Categoria(nombre="Tecnología", descripcion="Programación y computación."),
                ]
            )
            db.session.commit()

        if Libro.query.count() == 0:
            admin = Usuario.query.filter_by(username="admin").first()
            categorias = {c.nombre: c for c in Categoria.query.all()}
            db.session.add_all(
                [
                    Libro(
                        titulo="Cien años de soledad",
                        autor="Gabriel García Márquez",
                        anio=1967,
                        descripcion="Saga de la familia Buendía en Macondo.",
                        usuario_id=admin.id,
                        categoria_id=categorias["Ficción"].id,
                    ),
                    Libro(
                        titulo="Cosmos",
                        autor="Carl Sagan",
                        anio=1980,
                        descripcion="Un viaje por el universo y la ciencia.",
                        usuario_id=admin.id,
                        categoria_id=categorias["Ciencia"].id,
                    ),
                ]
            )

        db.session.commit()
        click.echo("Base de datos bd_biblioteca inicializada correctamente.")
        click.echo("Usuario administrador: admin / admin123")

    return app
