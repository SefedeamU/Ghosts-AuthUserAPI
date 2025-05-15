from fastapi import FastAPI
from app.api.auth_routes import router as auth_router
from app.api.user_routes import router as user_router
from app.api.address_routes import router as address_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(address_router, prefix="/addresses", tags=["addresses"])