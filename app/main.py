from datetime import time
from sqlite3 import OperationalError
from fastapi import FastAPI
from app.api.auth_routes import router as auth_router
from app.api.user_routes import router as user_router
from app.api.address_routes import router as address_router

from app.db.base import Base
from app.db.session import engine

for _ in range(10):
    try:
        Base.metadata.create_all(bind=engine)
        break
    except OperationalError:
        print("Esperando a que la base de datos esté lista...")
        time.sleep(2)
else:
    raise RuntimeError("No se pudo conectar a la base de datos después de varios intentos.")
app = FastAPI(
    title="Ghosts: Auth User - API",
    description="API for user authentication and users with addresses.",
    version="1.0.0"
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(address_router, prefix="/addresses", tags=["Addresses"])