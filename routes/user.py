from .mysql_data import mysql, approval_pdir, SESSION_TOKEN_HEADER, USER_ID_HEADER
from .token import hash_text, get_token, db_valid_token
from flask import Blueprint, request, jsonify
import binascii
import pymysql
import base64
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

    with mysql.get_db().cursor() as cursor:
        query = ("INSERT INTO users "
                 "(email, password, name, paternal_surname, maternal_surname, phone_number)"
                 " values (%s, %s, %s, %s, %s, %s)")
        try:
            cursor.execute(query, (email, hashed_password, name, paternal, maternal, phone))
        except pymysql.err.IntegrityError:
            return jsonify({"message": "El correo ya esta registrado"}), 401

    mysql.get_db().commit()

    return jsonify({"message": "Registro exitoso"}), 200


@user_bp.route("/request_approval", methods=["POST"])
def request_approval():
    user_id = request.headers.get(USER_ID_HEADER)
    session_token = request.headers.get(SESSION_TOKEN_HEADER)
    if not db_valid_token(user_id, session_token):
        return jsonify({"message": "La sesión ha expirado o los headers no se encontraron"}), 400

    data = request.get_json()
    photo = data.get("photo")
    if not photo or not isinstance(photo, str):
        return jsonify({"message": "Se requiere del comprobante"}), 400

    try:
        with open(approval_pdir.joinpath(f"{user_id}.jpeg"), "wb") as image:
            image_data = base64.decodebytes(photo.encode("utf-8"))
            image.write(image_data)
    except binascii.Error:
        return jsonify({"message": "Datos de imagen inválidos"}), 400

    return jsonify({"message": "Archivo recibido"}), 200


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
            "message": "Sesión iniciada",
            "user_id": user[0],
            "token": t
        }), 200

    return jsonify({"message": "Correo o contraseña incorrectos"}), 401
