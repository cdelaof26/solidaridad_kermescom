from .mysql_data import mysql, SESSION_TOKEN_HEADER
from flask import Blueprint, request, jsonify
import secrets
import hashlib


token_bp = Blueprint("token", __name__)


def hash_text(text: str, trim: bool = False):
    if not trim:
        return hashlib.sha256(text.encode()).hexdigest()
    return hashlib.sha256(text.encode()).hexdigest()[:20]


def get_token():
    token = secrets.token_hex(32)
    return hash_text(token, True)


def db_valid_token(user_id, session_token) -> bool:
    with mysql.get_db().cursor() as cursor:
        query = "SELECT email FROM users WHERE user_id = %s AND session_token = %s AND session_expires > NOW();"
        cursor.execute(query, (user_id, session_token))
        user = cursor.fetchone()

    if user:
        return True
    return False


@token_bp.route("/validate_token", methods=["POST"])
def validate_token():
    user_id = request.headers.get("User-Id")
    session_token = request.headers.get("Session-Token")

    if not user_id or not session_token:
        return jsonify({"message": "User ID and session token are required"}), 400

    if db_valid_token(user_id, session_token):
        return jsonify({"message": "Token is valid"}), 200

    return jsonify({"message": "La sesión expiró o los datos no son correctos. Inicia sesión de nuevo"}), 400


def update_token(session_token):
    if not session_token:
        return False

    with mysql.get_db().cursor() as cursor:
        query = "UPDATE users SET session_expires = NOW() + INTERVAL 59 MINUTE WHERE session_token = %s;"
        cursor.execute(query, (session_token,))

    mysql.get_db().commit()

    return True


def db_can_account_operate(session_token):
    with mysql.get_db().cursor() as cursor:
        query = "SELECT * from users WHERE session_token = %s AND can_operate = true;"
        cursor.execute(query, (session_token,))
        user = cursor.fetchone()

    if user:
        return True
    return False


@token_bp.route("/generate_token", methods=["GET"])
def generate_token_route():
    token = get_token()
    return jsonify({"token": token}), 200
