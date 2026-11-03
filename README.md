# Biblioteca Digital - Flask

Aplicación web para gestionar una biblioteca: usuarios, categorías y libros.
Usa Flask, SQLite (base `bd_biblioteca`), Flask-Login, Bootstrap 5 y el patrón
**Application Factory** con **Blueprints**.

## Instalación

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Crear la base de datos y el administrador

```bash
flask init-db
```

Usuario administrador: `admin` / `admin123`

## Ejecutar

```bash
flask run
```

Abrir en el navegador: http://127.0.0.1:5000

## Estructura

```
app/
  __init__.py        # create_app() - Application Factory
  extensions.py      # db y login_manager
  models.py          # Usuario, Categoria, Libro
  decorators.py      # admin_required, propietario_o_admin
  blueprints/
    main/            # página principal
    auth/            # login y logout
    usuarios/        # CRUD de usuarios (admin)
    categorias/      # CRUD de categorías (admin)
    libros/          # CRUD de libros
  templates/         # plantillas HTML
  static/css/        # estilos
database/schema.sql  # script SQL de la base de datos
docs/capturas/       # capturas de pantalla
```

## Modelo de datos

- `usuarios` (id, nombre, username, email, password_hash, rol, fecha_registro)
- `categorias` (id, nombre, descripcion, fecha_creacion)
- `libros` (id, titulo, autor, anio, descripcion, disponible, fecha_registro,
  usuario_id -> usuarios.id, categoria_id -> categorias.id)
