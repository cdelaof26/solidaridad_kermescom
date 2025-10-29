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


### Endpoints

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

Response: JSON
{
    "message": "Signup successful"
}
</pre>

<pre>
/login [POST]

Body: JSON
{
    "email": "",
    "password": "",
    "name": "",
    "paternal": "",
    "maternal": "",
    "phone": [number]
}

Response: JSON
{
    "message": "Login successful",
    "token": "23a3aea28f298dfe8e4d",
    "user_id": [number]
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
