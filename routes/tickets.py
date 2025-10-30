from .token import register_token, db_valid_token, update_token
from .mysql_data import mysql, SESSION_TOKEN_HEADER, USER_ID_HEADER
from flask import Blueprint, request, jsonify
import re

tickets_bp = Blueprint("tickets", __name__)


def tuple_to_ticket(t: tuple) -> dict:
    return {
        "ticket_id": t[0],
        "product_id": t[1],
        "user_id": t[2],
        "amount": t[3],
        "total": t[4],
        "requester_name": t[5],
        "phone_number": t[6],
        "directions": t[7],
        "open": t[8],
        "feedback": t[9]
    }


@tickets_bp.route("/list_my_requests", methods=["GET"])
def list_my_tickets():
    session_token = request.headers.get(SESSION_TOKEN_HEADER)
    token_id = register_token(session_token)
    if token_id is None:
        return jsonify({"message": "Se requiere de un token único"}), 400

    with mysql.get_db().cursor() as cursor:
        query = ("SELECT ticket_id, product_id, user_id, amount, "
                 "total, requester_name, phone_number, directions, "
                 "open, feedback FROM ticket WHERE token_id = %s;")
        cursor.execute(query, (token_id, ))
        tickets = cursor.fetchall()

    return [tuple_to_ticket(t) for t in tickets], 200


@tickets_bp.route("/list_requests", methods=["GET"])
def list_tickets():
    user_id = request.headers.get(USER_ID_HEADER)
    session_token = request.headers.get(SESSION_TOKEN_HEADER)
    if not db_valid_token(user_id, session_token):
        return jsonify({"message": "La sesión ha expirado o los headers no se encontraron"}), 400

    with mysql.get_db().cursor() as cursor:
        query = ("SELECT ticket_id, product_id, user_id, amount, "
                 "total, requester_name, phone_number, directions, "
                 "open, feedback FROM ticket WHERE token_id = %s;")
        cursor.execute(query, (user_id,))
        tickets = cursor.fetchall()

    return [tuple_to_ticket(t) for t in tickets], 200


@tickets_bp.route("/request_product", methods=["POST"])
def request_product():
    session_token = request.headers.get(SESSION_TOKEN_HEADER)
    token_id = register_token(session_token)
    if token_id is None:
        return jsonify({"message": "Se requiere de un token único"}), 400

    data = request.get_json()
    product_id = data["product_id"]
    amount = data["amount"]
    requester_name = data["requester_name"]
    phone = data["phone"]
    directions = data["directions"]
    if directions is None:
        directions = ""

    if not product_id:
        return jsonify({"message": "Se requiere de un id de producto"}), 400

    if (not amount or re.sub(r"\d+", "", str(amount)) != ""
            or not isinstance(amount, int) or amount < 0 or amount > 5):
        return jsonify({"message": "Se requiere una cantidad númerica especifica mayor que cero y menor que 6"}), 400

    if not requester_name or not phone:
        return jsonify({"message": "Se requiere nombre y número de un receptor"}), 400

    with mysql.get_db().cursor() as cursor:
        query = "SELECT user_id, price, available FROM stock WHERE product_id = %s AND available >= %s;"
        cursor.execute(query, (product_id, amount))
        product = cursor.fetchone()

    if not product:
        return jsonify({"message": "El producto no tiene existencias suficientes"}), 400

    with mysql.get_db().cursor() as cursor:
        query = ("INSERT INTO ticket "
                 "(product_id, token_id, user_id, amount, total, requester_name, phone_number, directions) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(
            query,
            (product_id, token_id, product[0], amount, amount * product[1], requester_name, phone, directions)
        )

        query = "UPDATE stock SET available = %s WHERE product_id = %s;"
        cursor.execute(query, (product[2] - amount, product_id))

    mysql.get_db().commit()

    if not update_token(session_token):
        return jsonify({"message": "Internal error while refreshing token"}), 500

    return jsonify({"message": "Ticket abierto"}), 200
