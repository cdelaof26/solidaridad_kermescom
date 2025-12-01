from .token import get_token, db_valid_token, db_can_account_operate, update_token
from .mysql_data import mysql, pdir, SESSION_TOKEN_HEADER, USER_ID_HEADER
from flask import Blueprint, request, jsonify
from pathlib import Path
import re

products_bp = Blueprint("products", __name__)


def validate_product(required_product_id: bool):
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

    if required_product_id:
        if not isinstance(product_id, int) or product_id < 0:
            return jsonify({"message": "El id de producto es inválido"}), 400

    if name is None or description is None:
        return jsonify({"message": "Se requiere de un nombre y descripción para la publicación"}), 400

    if price is None or available is None:
        return jsonify({"message": "Se requiere de un precio y cantidad disponible"}), 400

    if not isinstance(available, int) or (not isinstance(price, float) and not isinstance(price, int)):
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
        "price": t[2],
        "available": t[3],
        "description": t[4],
        "photo_dir": t[5]
    }


def processed_products(products: tuple, add_code: bool = True):
    products = [tuple_to_product(p) for p in products]

    for product in products:
        if "photo_dir" not in product:
            continue

        photo_dir = Path(product["photo_dir"])
        product["photos"] = len([e for e in photo_dir.iterdir()
                                 if e.is_file() and re.sub(r"\d+", "", e.name) == ""])
        product.pop("photo_dir")

    if add_code:
        return products, 200
    return products


def _get_product_photo(directory: str, index: int):
    photo_dir = Path(directory)
    photos = [e for e in photo_dir.iterdir() if e.is_file() and re.sub(r"\d+", "", e.name) == ""]
    if index > len(photos):
        raise ValueError("Invalid index")

    with open(photos[index], "r") as file:
        return file.read()


@products_bp.route("/products", methods=["POST"])
def list_products():
    data = request.get_json()
    pagination = True if data else False

    page, page_size = None, None
    if pagination:
        page = data.get("page")
        page_size = data.get("page_size")
        if page is not None and (not isinstance(page, int) or page <= 0):
            return jsonify({"message": "El número de página debe ser un número entero positivo"}), 400
        if page_size is not None and (not isinstance(page_size, int) or page_size <= 0):
            return jsonify({"message": "El tamaño de página debe ser un número entero positivo"}), 400

    if page is None or page_size is None:
        with mysql.get_db().cursor() as cursor:
            query = "SELECT product_id, name, price, available, description, photo_dir FROM stock;"
            cursor.execute(query)
            products = cursor.fetchall()

        return processed_products(products)

    offset = (page - 1) * page_size

    with mysql.get_db().cursor() as cursor:
        query = "SELECT product_id, name, price, available, description, photo_dir FROM stock LIMIT %s OFFSET %s;"
        cursor.execute(query, (page_size, offset))
        products = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM stock;")
        total_count = cursor.fetchone()[0]

    total_pages = (total_count + page_size - 1) // page_size

    return jsonify({
        "products": processed_products(products, False),
        "total_products": total_count,
        "total_pages": total_pages,
        "page": page
    }), 200


@products_bp.route("/product", methods=["POST"])
def get_product():
    data = request.get_json()
    product_id = data.get("product_id")
    if not isinstance(product_id, int) or product_id < 0:
        return jsonify({"message": "El id de producto es inválido"}), 400

    with mysql.get_db().cursor() as cursor:
        query = "SELECT product_id, name, price, available, description, photo_dir FROM stock WHERE product_id = %s;"
        cursor.execute(query, (product_id, ))
        product = cursor.fetchone()
        if not product:
            return jsonify({"message": f"El producto {product_id} no existe"}), 404

    return processed_products((product, ), False)[0], 200


@products_bp.route("/product_photo", methods=["POST"])
def get_product_photo():
    data = request.get_json()
    product_id = data.get("product_id")
    photo = data.get("photo")

    if not isinstance(product_id, int) or product_id < 0:
        return jsonify({"message": "El id de producto es inválido"}), 400

    if not isinstance(photo, int) or photo < 0:
        return jsonify({"message": "El número de foto debe ser un entero positivo"}), 400

    with mysql.get_db().cursor() as cursor:
        query = "SELECT photo_dir FROM stock WHERE product_id = %s;"
        cursor.execute(query, (product_id, ))
        product = cursor.fetchone()
        if not product:
            return jsonify({"message": f"El producto {product_id} no existe"}), 404

    try:
        return jsonify({"photo": _get_product_photo(product[0], photo)}), 200
    except ValueError:
        return jsonify({"message": "El número de fotografía es inválido"}), 400


@products_bp.route("/my_products", methods=["GET"])
def list_user_products():
    user_id = request.headers.get(USER_ID_HEADER)
    session_token = request.headers.get(SESSION_TOKEN_HEADER)
    if not db_valid_token(user_id, session_token):
        return jsonify({"message": "La sesión ha expirado o los headers no se encontraron"}), 400

    with mysql.get_db().cursor() as cursor:
        query = "SELECT product_id, name, price, available, description, photo_dir FROM stock WHERE user_id = %s;"
        cursor.execute(query, (user_id, ))
        products = cursor.fetchall()

    if not update_token(session_token):
        return jsonify({"message": "Internal error while refreshing token"}), 500

    return processed_products(products)


@products_bp.route("/add_product", methods=["POST"])
def add_product():
    data = validate_product(False)
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
    data = validate_product(True)
    if len(data) == 2:
        return data

    user_id, session_token, product_id, name, description, price, available, photos = data

    with mysql.get_db().cursor() as cursor:
        query = "SELECT photo_dir, user_id FROM stock WHERE product_id = %s;"
        cursor.execute(query, (product_id, ))
        product = cursor.fetchone()

    if not product:
        return jsonify({"message": f"El producto {product_id} no existe"}), 404

    if str(product[1]) != str(user_id):
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

    if not isinstance(product_id, int) or product_id < 0:
        return jsonify({"message": "El id de producto es inválido"}), 400

    with mysql.get_db().cursor() as cursor:
        query = "SELECT photo_dir, user_id FROM stock WHERE product_id = %s;"
        cursor.execute(query, (product_id, ))
        product = cursor.fetchone()

    if not product:
        return jsonify({"message": f"El producto {product_id} no existe"}), 404

    if str(product[1]) != str(user_id):
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
