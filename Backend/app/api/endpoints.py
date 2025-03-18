from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse

from app.models.schemas import LoginData, TokenResponse, UserInfo

from app.services.auth import(
    authenticate_odoo, create_access_token,
    verify_token, get_odoo_model
)

router = APIRouter(prefix="/api")

@router.post("/login", response_model=TokenResponse)
def login(data: LoginData):
    try:
        #Autenticar con odoo
        auth_result = authenticate_odoo(data.username, data.password)
        uid = auth_result["uid"]
        user_info = auth_result["user_info"]

        #crear token de acceso
        token = create_access_token(
            {"sub": data.username, "uid": uid},
            data.password
        )

        #preparar respuesta
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "name": user_info['name'],
                "email": user_info.get('email', ''),
                "role": "Usuario Odoo"
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail":  f"Error interno: {str(e)}"})
    
@router.get("/user-activities")
async def get_user_Activities(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer"):
        raise HTTPException(status_code=401, detail="Token de autenticacion requerido")
    
    # Extraer y verificar token
    token = authorization.split(" ")[1]
    user_data = verify_token(token)
    
    # Obtener actividades de Odoo
    model_name = "product.template"
    fields = ["name", "description", "list_price", "type"]
    
    # Agregar logs para debugging
    print(f"UID: {user_data['uid']}")
    print(f"Session ID: {user_data['session_id']}")
    print(f"Password disponible: {'Si' if user_data['password'] else 'No'}")
    
    try:
        activities = get_odoo_model(
            user_data["uid"],
            user_data["password"],
            model_name,
            fields
        )
        return activities
    except Exception as e:
        print(f"Error al obtener actividades: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener actividades: {str(e)}")