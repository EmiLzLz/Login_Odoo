#app/config.py
from datetime import timedelta
import os

#configuracion de la API
API_PREFIX = "/api"

#configuracion de CORS
CORS_ORIGINS = ["*"] # en produccion, esto se limita a los dominios frontend

#configuracion de Odoo
ODOO_URL = os.getenv("ODOO_URL", "http://216.238.79.93:8069")
ODOO_DB = os.getenv("ODOO_DB", "ADPMX")

#Configuracion JWT
SECRET_KEY = os.getenv("SECRET_KEY", "clave_super_secreta") # Esto se canvia en produccion
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

#Almacenamiento de sesiones (temporal, en memoria)
#En una aplicacion mas grande, esto deberia ser una base de datos
sessions = {}