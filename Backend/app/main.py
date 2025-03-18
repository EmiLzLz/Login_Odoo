from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.api import router

#crear aplicacion FastAPI
app = FastAPI(title="Odoo Login API")

#configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Incluir las rutas de la API
app.include_router(router)

#para facilitas las pruebas cuando se ejecuta directamente 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
# Para iniciar: uvicorn main:app --reload