# Solidaridad KermESCOM

Solidaridad KermESCOM es un proyecto con el objetivo
de poner en contacto a vendedores y compradores.

[Más información aquí](sys_requ.md)

### Desarrollo

#### Instalar requerimientos
```bash
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
