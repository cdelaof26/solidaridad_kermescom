from flask import Flask, request, jsonify
from flaskext.mysql import MySQL
from pathlib import Path
import logging
import secrets
import hashlib
import os
import re


SESSION_TOKEN_HEADER = "Session-Token"
USER_ID_HEADER = "User-Id"

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

app.config["PDIR"] = Path(p)
if not app.config["PDIR"].exists():
    logging.warning(f"Directory {app.config["PDIR"]} doesn't exist")
    app.config["PDIR"].mkdir(parents=True, exist_ok=True)
    logging.warning(f"Directory {app.config["PDIR"]} was created")

mysql = MySQL(app)


def hash_text(text: str, trim: bool = False):
    if not trim:
        return hashlib.sha256(text.encode()).hexdigest()
    return hashlib.sha256(text.encode()).hexdigest()[:20]


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    paternal = data.get("paternal")
    maternal = data.get("maternal")
    phone = data.get("phone")

    if not email or not password:
        return jsonify({"message": "Correo y contraseña requeridos"}), 400

    if not name or not paternal or not maternal:
        return jsonify({"message": "El nombre y apellidos son requeridos"}), 400

    if not phone or re.sub(r"\d{10}", "", str(phone)) != "":
        return jsonify({"message": "Se requiere de un número de teléfono de 10 digitos"}), 400

    hashed_password = hash_text(password, True)
    _p = app.config["PDIR"].joinpath(get_token())
    _p.mkdir(parents=True)
    _p = str(_p)

    with mysql.get_db().cursor() as cursor:
        query = ("INSERT INTO users "
                 "(email, password, name, paternal_surname, maternal_surname, phone_number, photo_dir)"
                 " values (%s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(query, (email, hashed_password, name, paternal, maternal, phone, _p))

    mysql.get_db().commit()

    return jsonify({"message": "Signup successful"}), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Correo y contraseña requeridos"}), 400

    hashed_password = hash_text(password, True)

    with mysql.get_db().cursor() as cursor:
        query = "SELECT * FROM users WHERE email = %s AND password = %s"
        cursor.execute(query, (email, hashed_password))
        user = cursor.fetchone()

    if user:
        t = get_token()
        with mysql.get_db().cursor() as cursor:
            query = ("UPDATE users SET session_token = %s, "
                     "session_expires = NOW() + INTERVAL 30 MINUTE WHERE email = %s;")
            cursor.execute(query, (t, email))
        mysql.get_db().commit()

        return jsonify({
            "message": "Login successful",
            "user_id": user[0],
            "token": t
        }), 200

    return jsonify({"message": "Correo o contraseña incorrectos"}), 401


def get_token():
    token = secrets.token_hex(32)
    return hash_text(token, True)


@app.route("/validate_token", methods=["POST"])
def validate_token():
    user_id = request.headers.get("User-Id")
    session_token = request.headers.get("Session-Token")

    if not user_id or not session_token:
        return jsonify({"message": "User ID and session token are required"}), 400

    with mysql.get_db().cursor() as cursor:
        query = "SELECT email FROM users WHERE user_id = %s AND session_token = %s AND session_expires > NOW();"
        cursor.execute(query, (user_id, session_token))
        user = cursor.fetchone()

    if user:
        return jsonify({"message": "Token is valid"}), 200

    return jsonify({"message": "La sesión expiró o los datos no son correctos. Inicia sesión de nuevo"}), 400


def update_token():
    session_token = request.headers.get(SESSION_TOKEN_HEADER)
    if not session_token:
        return jsonify({"message": "Session token is required"}), 400

    with mysql.get_db().cursor() as cursor:
        query = "UPDATE users SET session_expires = NOW() + INTERVAL 30 MINUTE WHERE session_token = %s;"
        cursor.execute(query, (session_token,))

    mysql.get_db().commit()

    return jsonify({"message": "Token updated successfully"}), 200


@app.route("/generate_token", methods=["GET"])
def generate_token_route():
    token = get_token()
    return jsonify({"token": token}), 200


if __name__ == "__main__":
    app.run()
