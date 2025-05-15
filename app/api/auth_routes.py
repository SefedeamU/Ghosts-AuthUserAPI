from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import decode_access_token, hash_password
from app.models.user_model import User
from app.schemas.auth_schema import UserRegister, UserLogin, AuthResponse
from app.api.deps import get_db
from app.crud.auth_crud import login, register

router = APIRouter()

@router.post("/login", response_model=AuthResponse)
def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    try:
        result = login(db, user_in)
        user = result["user"]
        return {
            "id": user.id,
            "user_rol": user.user_rol,
            "access_token": result["access_token"]
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

@router.post("/register", response_model=AuthResponse)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    try:
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=hash_password(user_in.password),
            user_rol="customer"
        )
        result = register(db, db_user)
        return {
            "id": result.id,
            "user_rol": result.user_rol,
            "access_token": result.access_token
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

@router.post("/verify-token")
def verify_token(Authorization: str = Header(...)):
    token = Authorization.split(" ")[1] if " " in Authorization else Authorization
    result = decode_access_token(token)
    return result