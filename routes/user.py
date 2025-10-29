from flask import Blueprint, request, jsonify
from .token import hash_text, get_token
from .mysql_data import mysql, pdir
import re

user_bp = Blueprint("user", __name__)


@user_bp.route("/signup", methods=["POST"])
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
    _p = pdir.joinpath(get_token())
    _p.mkdir(parents=True)
    _p = str(_p)

    with mysql.get_db().cursor() as cursor:
        query = ("INSERT INTO users "
                 "(email, password, name, paternal_surname, maternal_surname, phone_number, photo_dir)"
                 " values (%s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(query, (email, hashed_password, name, paternal, maternal, phone, _p))

    mysql.get_db().commit()

    return jsonify({"message": "Signup successful"}), 200


@user_bp.route("/login", methods=["POST"])
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
