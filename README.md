# Solidaridad KermESCOM

Solidaridad KermESCOM es un proyecto con el objetivo
de poner en contacto a vendedores y compradores.

[Más información aquí](sys_requ.md)

### Desarrollo

#### Instalar requerimientos
```bash
cd solidaridad_kermescom

python3 -m pip install -r requirements.txt
```

#### Colocar variables de entorno
```bash
export MYSQL_HOST="localhost"
export MYSQL_USER="myUser1234"
export MYSQL_PASSWORD="myPassword1234"
# Directorio donde se guardarán las fotos subidas
export PHOTOS_DIR="/home/"
```

#### Iniciar servidor de desarrollo
```bash
flask --app main.py run
```

#### Deploy
```bash
# Ejecuta proyecto en segundo plano (puerto 8080)
nohup waitress-serve --call routes:create_app &
```

#### Aprobar cuenta manualmente
```mysql
UPDATE users SET can_operate = true WHERE user_id = X;
```


### Endpoints

<details>
    <summary>Usuario: /signup, /login</summary>
<pre>
/signup [POST]

Body: JSON
{
    "email": "",
    "password": "",
    "name": "",
    "paternal": "",
    "maternal": "",
    "phone": 
}

Todos los campos son requeridos

Response: JSON
{
    "message": "Registro exitoso"
}
</pre>


<pre>
/request_approval [POST]

Body: JSON
{
    "photo": "base64_photo_1"
}

Error: JSON
Si no hay una sesión activa
{
    "message": "La sesión ha expirado"
}

Si el campo "photo" no tiene datos base64 válidos, se responderá con 400
{
    "message": "Datos de imagen inválidos"
}

Response: JSON
{
    "message": "Archivo recibido"
}
</pre>

<pre>
/login [POST]

Body: JSON
{
    "email": "",
    "password": "",
}

Todos los campos son requeridos

Response: JSON
{
    "message": "Sesión iniciada",
    "token": "23a3aea28f298dfe8e4d",
    "user_id": [number]
}
</pre>
</details>



<details>
    <summary>Productos: /products, /my_products, /add_product, /edit_product, /delete_product</summary>


<pre>
/products [GET]

Body: None

Response: JSON
[
    {
        "available": [number],
        "description": "",
        "name": "",
        "photos": ["base64_photo_1", "base64_photo_2", ... ],
        "price": [number],
        "product_id": [number]
    },
    {
        "available": [number],
        "description": "",
        "name": "",
        "photos": ["base64_photo_1", "base64_photo_2", ... ],
        "price": [number],
        "product_id": [number]
    }
]
</pre>


<pre>
/my_products [GET]

Retorna los productos registrados por el usuario con sesión

Body: None

Error: JSON
Si no hay una sesión activa
{
    "message": "La sesión ha expirado"
}

Si la cuenta no se ha aprobado, se responderá con 401
{
    "message": "La cuenta aún no ha sido aprobada"
}

Response: JSON
Same as /products
</pre>

<pre>
/add_product [POST]

Body: JSON
{
    "name": "",
    "description": "",
    "price": [number],
    "available": [number],
    "photos": ["base64_photo_1", "base64_photo_2", ...]
}

Todos los campos son requeridos, excepto 'photos'

Error: JSON
Si no hay una sesión activa
{
    "message": "La sesión ha expirado"
}

Si la cuenta no se ha aprobado, se responderá con 401
{
    "message": "La cuenta aún no ha sido aprobada"
}

Response: JSON
{
    "message": "Producto agregado"
}
</pre>


<pre>
/edit_product [PUT]

Body: JSON
{
    "product_id": "",
    "name": "",
    "description": "",
    "price": [number],
    "available": [number],
    "photos": ["base64_photo_1", "base64_photo_2", ...]
}

Todos los campos son requeridos, excepto 'photos'

Error: JSON
Si no hay una sesión activa
{
    "message": "La sesión ha expirado"
}

Si la cuenta no se ha aprobado, se responderá con 401
{
    "message": "La cuenta aún no ha sido aprobada"
}

Si la cuenta no creo el producto, se responderá con 401
{
    "message": "El producto seleccionado (ID) no lo puede editar el usuario (ID)"
}

Response: JSON
{
    "message": "Producto editado"
}
</pre>


<pre>
/delete_product [DELETE]

Body: JSON
{
    "product_id": "",
}

Error: JSON
Si no hay una sesión activa
{
    "message": "La sesión ha expirado"
}

Si la cuenta no se ha aprobado, se responderá con 401
{
    "message": "La cuenta aún no ha sido aprobada"
}

Si la cuenta no creo el producto, se responderá con 401
{
    "message": "El producto seleccionado (ID) no lo puede editar el usuario (ID)"
}

Response: JSON
{
    "message": "Producto editado"
}
</pre>

</details>



<details>
    <summary>Tickets: /list_my_requests, /list_requests, /request_product, /generate_token</summary>

<pre>
/list_my_requests [GET]

Body: None

Error: JSON
Si no hay un token único
{
    "message": "Se requiere de un token único"
}

Response: JSON
[
    {
        "amount": [number],
        "directions": "",
        "feedback": [string or null],
        "open": [0 or 1],
        "phone_number": [number],
        "product_id": [number],
        "requester_name": "",
        "ticket_id": [number],
        "total": [number],
        "user_id": [number]
    }, ...
]
</pre>


<pre>
/list_requests [GET]

Body: None

Error: JSON
Si no hay una sesión activa
{
    "message": "La sesión ha expirado"
}

Si la cuenta no se ha aprobado, se responderá con 401
{
    "message": "La cuenta aún no ha sido aprobada"
}

Response: JSON
Same as /list_requests
</pre>

<pre>
/request_product [GET]

Body: JSON
{
    "product_id": "",
    "amount": [number],
    "requester_name": "",
    "phone": [number],
    "directions": ""
}

Error: JSON
Si no hay un token único
{
    "message": "Se requiere de un token único"
}

Response: JSON
{
    "message": "Ticket abierto"
}
</pre>

<pre>
/generate_token [GET]

Body: None

Response: JSON
{
    "token": "7cb54234bd5490fbcec4"
}
</pre>

</details>
