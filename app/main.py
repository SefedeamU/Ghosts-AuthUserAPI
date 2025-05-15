from fastapi import FastAPI
from app.api.auth_routes import router as auth_router
from app.api.user_routes import router as user_router
from app.api.address_routes import router as address_router

app = FastAPI(
     title="Ghosts: Auth User - API",
    description="API for user authentication and users with addresses.",
    version="1.0.0"
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(address_router, prefix="/addresses", tags=["Addresses"])