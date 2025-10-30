from .token import get_token, db_valid_token, db_can_account_operate, update_token
from .mysql_data import mysql, pdir, SESSION_TOKEN_HEADER, USER_ID_HEADER
from flask import Blueprint, request, jsonify
from pathlib import Path
import re

products_bp = Blueprint("products", __name__)


def validate_product():
    user_id = request.headers.get(USER_ID_HEADER)
    session_token = request.headers.get(SESSION_TOKEN_HEADER)
    if not db_valid_token(user_id, session_token):
        return jsonify({"message": "La sesión ha expirado o los headers no se encontraron"}), 400

    if not db_can_account_operate(session_token):
        return jsonify({"message": "La cuenta aún no ha sido aprobada"}), 401

    data = request.get_json()
    product_id = data.get("product_id")
    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    available = data.get("available")
    photos = data.get("photos")

    if not name or not description:
        return jsonify({"message": "Se requiere de un nombre y descripción para la publicación"}), 400

    if not price or not available:
        return jsonify({"message": "Se requiere de un precio y cantidad disponible"}), 400

    if not isinstance(price, int) or (not isinstance(available, float) and not isinstance(available, int)):
        return jsonify({"message": "El precio y la cantidad disponibles deben ser números positivos"}), 400

    if price < 0 or available < 0:
        return jsonify({
            "message": f"El valor para precio ({price}) o el valor de disponibles ({available}) no es valido"
        }), 400

    return user_id, session_token, product_id, name, description, price, available, photos


def tuple_to_product(t: tuple) -> dict:
    return {
        "product_id": t[0],
        "name": t[1],
        "description": t[2],
        "price": t[3],
        "available": t[4],
        "photo_dir": t[5]
    }


def processed_products(products: tuple):
    products = [tuple_to_product(p) for p in products]

    for product in products:
        photo_dir = Path(product["photo_dir"])
        product["photos"] = []
        for e in photo_dir.iterdir():
            if not e.is_file() or re.sub(r"\d+", "", e.name) != "":
                continue

            with open(e, "r") as file:
                product["photos"].append(file.read())

        product["photo_dir"] = None

    return products, 200


@products_bp.route("/products", methods=["GET"])
def list_products():
    with mysql.get_db().cursor() as cursor:
        query = "SELECT product_id, name, description, price, available, photo_dir FROM stock;"
        cursor.execute(query)
        products = cursor.fetchall()

    return processed_products(products)


@products_bp.route("/my_products", methods=["GET"])
def list_user_products():
    user_id = request.headers.get(USER_ID_HEADER)
    session_token = request.headers.get(SESSION_TOKEN_HEADER)
    if not db_valid_token(user_id, session_token):
        return jsonify({"message": "La sesión ha expirado o los headers no se encontraron"}), 400

    with mysql.get_db().cursor() as cursor:
        query = "SELECT product_id, name, description, price, available, photo_dir FROM stock WHERE user_id = %s;"
        cursor.execute(query, (user_id, ))
        products = cursor.fetchall()

    return processed_products(products)


@products_bp.route("/add_product", methods=["POST"])
def add_product():
    data = validate_product()
    if len(data) == 2:
        return data

    user_id, session_token, product_id, name, description, price, available, photos = data

    photo_dir = pdir.joinpath(get_token())
    photo_dir.mkdir(parents=True)

    if photos:
        if not isinstance(photos, list):
            return jsonify({"message": "'photos' must be a list"}), 400

        for i, p in enumerate(photos):
            with open(photo_dir.joinpath(f"{i}"), "w") as file:
                file.write(p)

    photo_dir = str(photo_dir)

    with mysql.get_db().cursor() as cursor:
        query = ("INSERT INTO stock (user_id, name, description, price, available, photo_dir) "
                 "values (%s, %s, %s, %s, %s, %s)")
        cursor.execute(query, (user_id, name, description, price, available, photo_dir))

    mysql.get_db().commit()

    if not update_token(session_token):
        return jsonify({"message": "Internal error while refreshing token"}), 500

    return jsonify({"message": "Producto agregado"}), 200


@products_bp.route("/edit_product", methods=["PUT"])
def edit_product():
    data = validate_product()
    if len(data) == 2:
        return data

    user_id, session_token, product_id, name, description, price, available, photos = data

    with mysql.get_db().cursor() as cursor:
        query = "SELECT photo_dir, user_id FROM stock WHERE product_id = %s;"
        cursor.execute(query, (product_id, ))
        product = cursor.fetchone()

    if not product:
        return jsonify({"message": f"El producto {product_id} no existe"}), 404

    if product[1] != user_id:
        return jsonify({
            "message": f"El producto seleccionado ({product_id}) no lo puede editar el usuario ({user_id})"
        }), 401

    photo_dir = Path(product[0])

    if photos:
        if not isinstance(photos, list):
            return jsonify({"message": "'photos' must be a list"}), 400

        for i, p in enumerate(photos):
            with open(photo_dir.joinpath(f"{i}"), "w") as file:
                file.write(p)
    else:
        for e in photo_dir.iterdir():
            if e.is_file():
                e.unlink()

    with mysql.get_db().cursor() as cursor:
        query = "UPDATE stock SET name = %s, description = %s, price = %s, available = %s WHERE product_id = %s;"
        cursor.execute(query, (name, description, price, available, product_id))

    mysql.get_db().commit()

    if not update_token(session_token):
        return jsonify({"message": "Internal error while refreshing token"}), 500

    return jsonify({"message": "Producto editado"}), 200


@products_bp.route("/delete_product", methods=["DELETE"])
def delete_product():
    user_id = request.headers.get(USER_ID_HEADER)
    session_token = request.headers.get(SESSION_TOKEN_HEADER)
    if not db_valid_token(user_id, session_token):
        return jsonify({"message": "La sesión ha expirado o los headers no se encontraron"}), 400

    if not db_can_account_operate(session_token):
        return jsonify({"message": "La cuenta aún no ha sido aprobada"}), 401

    data = request.get_json()
    product_id = data.get("product_id")

    with mysql.get_db().cursor() as cursor:
        query = "SELECT photo_dir, user_id FROM stock WHERE product_id = %s;"
        cursor.execute(query, (product_id, ))
        product = cursor.fetchone()

    if not product:
        return jsonify({"message": f"El producto {product_id} no existe"}), 404

    if product[1] != user_id:
        return jsonify({
            "message": f"El producto seleccionado ({product_id}) no lo puede editar el usuario ({user_id})"
        }), 401

    photo_dir = Path(product[0])
    for e in photo_dir.iterdir():
        if e.is_file():
            e.unlink()

    with mysql.get_db().cursor() as cursor:
        query = "DELETE FROM stock WHERE product_id = %s;"
        cursor.execute(query, (product_id, ))

    mysql.get_db().commit()

    if not update_token(session_token):
        return jsonify({"message": "Internal error while refreshing token"}), 500

    return jsonify({"message": "Producto eliminado"}), 200
