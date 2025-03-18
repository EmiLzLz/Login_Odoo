import secrets
import xmlrpc.client
from datetime import datetime
from fastapi import HTTPException
from jose import JWTError, jwt

from app.config import (
    ODOO_URL, ODOO_DB, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE, sessions
)

def create_access_token(data: dict, password: str):
    """Crea un token JWT con los datos del ususario y su sesion"""
    to_encode = data.copy()
    expire = datetime.utcnow() + ACCESS_TOKEN_EXPIRE
    to_encode.update({"exp": expire})

    #crear ID de sesion
    session_id = secrets.token_urlsafe(16)
    sessions[session_id] = {
        "password": password,
        "expires": expire
    }

    to_encode.update({"session": session_id})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    """Verifica y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        uid = payload.get("uid")
        session_id = payload.get("session")

        if not username or not uid or not session_id:
            raise HTTPException(status_code=401, detail="Token invalido")
        
        if session_id not in sessions:
            raise HTTPException(status_code=401, detail = "Sesion invalida")
        
        if datetime.utcnow() > sessions[session_id]["expires"]: 
            del sessions[session_id]
            raise HTTPException(status_code=401, detail="Sesion expirada")
        
        return{
            "username": username,
            "uid": uid,
            "session_id": session_id,
            "password": sessions[session_id]["password"]
        }
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")

def authenticate_odoo(username: str, password: str):
    """Autentica al usuario en Odoo y devuelve informacion relevante"""
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, username, password, {})

        if not uid:
            raise HTTPException(status_code=401, detail="Credenciales invalidas")
        
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        user_info = models.execute_kw(
            ODOO_DB, uid, password,
            'res.users', 'read',
            [uid],
            {'fields':['name','email','login']}
        )[0]

        return {
            "uid": uid,
            "user_info": user_info
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de autenticacion: {str(e)}")
    
def get_odoo_model(uid: int, password: str, model_name: str, fields: list, domain=None, limit=50):
    """Obtiene datos de un modelo de Odoo"""
    try:
        if domain is None:
            domain = []

        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        data = models.execute_kw(
            ODOO_DB, uid, password,
            model_name, "search_read",
            [domain],
            {
                "fields": fields,
                "limit": limit
            }
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos {str(e)}")