from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any

class LoginData(BaseModel):
    """Modelo para los datos de inicio de sesion"""""
    username: str
    password: str

class UserInfo(BaseModel):
    """Modelo para informacion del usuario"""
    name: str
    email: Optional[str] = None
    role: Optional[str] = "Usuario Odoo"

class TokenResponse(BaseModel):
    """Modelo para la respuesta de autenticacion"""
    access_token: str
    token_type: str = "bearer"
    user: UserInfo

class Activity(BaseModel):
    """Modelo para actividades/productos"""
    name: str
    description: Optional[str] = None
    list_price: Optional[float] = None
    type: Optional[str] = None