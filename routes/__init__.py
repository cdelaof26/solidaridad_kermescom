from .mysql_data import mysql, pdir
from flaskext.mysql import MySQL
from pathlib import Path
from flask import Flask
import logging
import os


def create_app():
    app = Flask(__name__)

    # MySQL configurations
    app.config["MYSQL_DATABASE_HOST"] = os.getenv("MYSQL_HOST")
    app.config["MYSQL_DATABASE_USER"] = os.getenv("MYSQL_USER")
    app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
    app.config["MYSQL_DATABASE_DB"] = "sol_db"
    p = os.getenv("PHOTOS_DIR")
    if p is None:
        logging.error("A directory must be specified (PHOTOS_DIR environment variable)")
        exit(1)

    mysql_data.pdir = Path(p)
    if not mysql_data.pdir.exists():
        logging.warning(f"Directory {mysql_data.pdir} doesn't exist")
        mysql_data.pdir.mkdir(parents=True, exist_ok=True)
        logging.warning(f"Directory {mysql_data.pdir} was created")

    mysql_data.mysql = MySQL(app)

    from .user import user_bp
    from .token import token_bp
    from .products import products_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(token_bp)
    app.register_blueprint(products_bp)

    return app
