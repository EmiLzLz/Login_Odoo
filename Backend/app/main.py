from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordBearer
import secrets
from fastapi.middleware.cors import CORSMiddleware
import xmlrpc.client
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi.responses import JSONResponse


app = FastAPI()
sessions = {}

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo para login
class LoginData(BaseModel):
    username: str
    password: str

# Configuración de Odoo
ODOO_URL = "http://216.238.79.93:8069"
ODOO_DB = "ADPMX"

# Claves para JWT
SECRET_KEY = "clave_super_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Función para generar token JWT
def create_access_token(data: dict, password: str, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    # Crear un ID de sesión
    session_id = secrets.token_urlsafe(16)
    sessions[session_id] = {
        "password": password,
        "expires": expire
    }
    
    to_encode.update({"session": session_id})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Modificar el endpoint de login
@app.post("/api/login")
def login(data: LoginData):
    try:
        # Conectar con Odoo para autenticar al usuario
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, data.username, data.password, {})
        
        if not uid:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        # Obtener información del usuario desde Odoo
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        user_info = models.execute_kw(
            ODOO_DB, uid, data.password,
            'res.users', 'read',
            [uid],
            {'fields': ['name', 'email', 'login']}
        )[0]
        
        # Crear token de acceso
        token = create_access_token(
            {"sub": data.username, "uid": uid},
            data.password
        )
        
        return {
            "access_token": token, 
            "token_type": "bearer",
            "user": {
                "name": user_info['name'],
                "email": user_info.get('email', ''),
                "role": "Usuario Odoo"  # Puedes obtener el rol real si lo necesitas
            }
        }
    
    except Exception as e:
        print(f"Error de login: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})




#endpoint actividades
@app.get("/api/user-activities")
async def get_user_activities(authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de autenticación requerido")
        
        # Extraer el token
        token = authorization.split(" ")[1]
        
        # Verificar y decodificar el token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            uid = payload.get("uid")
        except JWTError:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        
        print(f"Obteniendo actividades para el usuario {username} (UID: {uid})")

        # Obtener contraseña de la sesión
        session_id = payload.get("session")
        if not session_id or session_id not in sessions:
            raise HTTPException(status_code=401, detail="Sesión inválida")
        
        # Verificar expiración
        if datetime.utcnow() > sessions[session_id]["expires"]:
            del sessions[session_id]
            raise HTTPException(status_code=401, detail="Sesión expirada")
        
        password = sessions[session_id]["password"]
        
        # Conexión con Odoo
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        
        # Recuperar el modelo correcto que contiene las actividades o productos
        # (ajusta este nombre de modelo según tu estructura en Odoo)
        model_name = "product.template"  # o "tourism.activity" u otro modelo que uses
        
        # Intentar obtener actividades que el usuario puede ver/vender
        # No aplicamos filtros de dominio específicos y dejamos que las reglas de registro de Odoo
        # controlen qué puede ver el usuario basado en sus grupos
        activities = models.execute_kw(
            ODOO_DB, uid, password,  # Usar la contraseña recuperada
            model_name, "search_read",
            [[]],
            {
                "fields": ["name", "description", "list_price", "type"],
                "limit": 50
            }
        )
        
        print(f"Se encontraron {len(activities)} actividades para el usuario")
        return activities
        
    except Exception as e:
        print(f"Error al obtener actividades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Para iniciar: uvicorn main:app --reload