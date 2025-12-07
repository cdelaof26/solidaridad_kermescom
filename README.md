# Solidaridad KermESCOM

Solidaridad KermESCOM es un proyecto con el objetivo
de poner en contacto a vendedores y compradores.

[Más información aquí](sys_requ.md)

### Desarrollo

#### Requisitos
- Python 3.10 o posterior

#### Instalar requerimientos
```bash
# Clona el proyecto
git clone https://github.com/cdelaof26/solidaridad_kermescom.git

cd solidaridad_kermescom

# Instalación en paquetes globales
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
# Waitress requiere instalación: python3 -m pip install waitress
```

#### Unattended install in Debian systems
El archivo `debian_install.sh` es un script escrito en
bash y Python que tiene propósito realizar la instalación 
del sistema completo en un ambiente Debian con mínima 
interacción.

```bash
# Clona el proyecto
git clone https://github.com/cdelaof26/solidaridad_kermescom.git

cd solidaridad_kermescom

# Realiza la instalación
chmod +x debian_install.sh

# ./debian_install [start] [stop]
# [start]: operación sobre la cual iniciará (conforme a la siguiente tabla, columna "Argumento")
# [stop]:  operación con la cual terminará
# Ejemplos,
#   ./debian_install.sh 2
#      El script empezará en mysql_install y continuará hasta terminar con project_setup
#   ./debian_install.sh 3 3
#      El script solo ejecutará mysql_configure
#   ./debian_install.sh 2 4
#      El script ejecutará mysql_install, mysql_configure y database_setup

export ROOT_PASSWORD=mySecurePassword
export MYSQL_USER=myUser
export MYSQL_PASSWORD=myPassword

./debian_install.sh

# El script require de tres variables de entorno,
#  1. ROOT_PASSWORD: Es la contraseña que se le pondrá al usuario root de MySQL
#  2. MYSQL_USER: Es el usuario que se configurará aparte de root
#  3. MYSQL_PASSWORD: Es la contraseña del usuario que se configurará aparte de root
```

| Argumento | Nombre               | Descripción                                                                                                                         |
|-----------|----------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| `1`       | `dependency_install` | Instala las dependencias necesarias para ejecutar el proyecto (`wget`, `gnupg`, `python3`, `python3-pip`, `python3-venv`)           |
| `2`       | `mysql_install`      | Configura el repositorio para MySQL e instala `mysql-server`                                                                        |
| `3`       | `mysql_configure`    | Realiza las configuraciones correspondientes a `mysql_secure_install`, estas se pueden modificar desde [secmysql.sql](secmysql.sql) |
| `4`       | `database_setup`     | Crea la base de datos `sol_db` conforme a los contenidos de [database.sql](database.sql)                                            |
| `5`       | `project_setup`      | Crea un ambiente Python (`venv`) e instala las dependencias conforme a los contenidos de [requirements.txt](requirements.txt)       |


#### Aprobar cuenta manualmente
```mysql
UPDATE users SET can_operate = true WHERE user_id = X;
```

#### Aprobar cuenta automáticamente sin validación
```bash
# Agrega la variable de entorno (valores "yes" o "no")
# Se puede cambiar en runtime.
export AUTO_APPROVE="yes"
```


### Headers

| Nombre en backend      | Header          | Descripción                                                                                    |
|------------------------|-----------------|------------------------------------------------------------------------------------------------|
| `SESSION_TOKEN_HEADER` | `Session-Token` | Token generado por el sistema para inicio de sesión persistente y autenticación sin contraseña |
| `USER_ID_HEADER`       | `User-Id`       | Identificador único del usuario registrado                                                     |
| `TOKEN_HEADER`         | `SKE-Token`     | Token único generado por el sistema para el seguimiento de usuarios no registrados             |


### Endpoints

<details>
    <summary>Usuario: /signup, /login, /logout</summary>
<pre>
/signup [POST]

Body: JSON
{
    "email": [string],
    "password": [string],
    "name": [string],
    "paternal": [string],
    "maternal": [string],
    "phone": [number]
}

Todos los campos son requeridos

Response: JSON
{
    "message": "Registro exitoso"
}
</pre>


<pre>
/login [POST]

Body: JSON
{
    "email": [string],
    "password": [string],
}

Todos los campos son requeridos

Response: JSON
{
    "message": "Sesión iniciada",
    "token": "23a3aea28f298dfe8e4d",
    "user_id": [number]
}
</pre>


<pre>
/logout [POST]

Body: None

Error: JSON
Si no hay una sesión activa
{
    "message": "La sesión ha expirado"
}

Response: JSON
{
    "message": "Sesión terminada"
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

</details>



<details>
    <summary>Productos: /products, /product, /my_products, /add_product, /edit_product, /delete_product</summary>


<pre>
/products [POST]

Body: [OPTIONAL] JSON
{
    "page_size": [number],
    "page": [number]
}

Response: JSON
[
    {
        "available": [number],
        "description": [string],
        "name": [string],
        "photos": [number],
        "price": [number],
        "product_id": [number]
    },
    {
        "available": [number],
        "description": [string],
        "name": [string],
        "photos": [number],
        "price": [number],
        "product_id": [number]
    }
]
</pre>


<pre>
/product [POST]

Body: JSON
{
    "product_id": [number]
}

Response: JSON
{
    "available": [number],
    "description": [string],
    "name": [string],
    "photos": [number],
    "price": [number],
    "product_id": [number]
}
</pre>


<pre>
/product_photo [POST]

Body: JSON
{
    "product_id": [number],
    "photo": [number]
}

Response: JSON
{
    "photo": "base64data"
}
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
    "name": [string],
    "description": [string],
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
    "product_id": [string],
    "name": [string],
    "description": [string],
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
    "product_id": [string],
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
    <summary>Tickets: /list_my_requests, /list_requests, /request_product, /add_feedback, /close_request, /close_my_request, /generate_token</summary>

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
        "directions": [string],
        "feedback": [string or null],
        "open": [0 or 1],
        "phone_number": [number],
        "product_id": [number],
        "requester_name": [string],
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
/request_product [POST]

Body: JSON
{
    "product_id": [string],
    "amount": [number],
    "requester_name": [string],
    "phone": [number],
    "directions": [string]
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
/add_feedback [POST]

Body: JSON
{
    "ticket_id": [number],
    "feedback": [string]
}

Error: JSON
Si no hay una sesión activa
{
    "message": "La sesión ha expirado"
}

Response: JSON
{
    "message": "Feedback agregado"
}
</pre>

<pre>
/close_request [POST]

Body: JSON
{
    "ticket_id": [number]
}

Error: JSON
Si no hay una sesión activa
{
    "message": "La sesión ha expirado"
}

Response: JSON
{
    "message": "Ticket cerrado"
}
</pre>

<pre>
/close_my_request [POST]

Body: JSON
{
    "ticket_id": [number]
}

Error: JSON
Si no hay un token único
{
    "message": "Se requiere de un token único"
}

Si el token único no coincide con el ticket_id
{
    "message": "W h a t"
}

Response: JSON
{
    "message": "Ticket cerrado"
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
