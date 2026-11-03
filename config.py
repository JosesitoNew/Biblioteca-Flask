import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "biblioteca-clave-secreta")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "bd_biblioteca.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NOMBRE_SITIO = "Biblioteca Digital"
    NOMBRE_INSTITUCION = "TEM-742 · Tecnologías Emergentes II"
