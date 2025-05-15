from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import EmailStr, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.security import decode_access_token, hash_password
from app.models.user_model import User
from app.schemas.auth_schema import UserRegister, UserLogin, AuthResponse
from app.api.deps import get_db
from app.crud.auth_crud import login, register

router = APIRouter()

def validate_login_fields(user_in: UserLogin):
    if not isinstance(user_in.email, str) or not user_in.email.strip():
        raise HTTPException(status_code=422, detail="The 'email' field is required and must be a non-empty string.")
    try:
        EmailStr.validate(user_in.email)
    except ValidationError:
        raise HTTPException(status_code=422, detail="The 'email' field must be a valid email address.")
    if not isinstance(user_in.password, str) or not user_in.password.strip():
        raise HTTPException(status_code=422, detail="The 'password' field is required and must be a non-empty string.")

def validate_register_fields(user_in: UserRegister):
    if not isinstance(user_in.email, str) or not user_in.email.strip():
        raise HTTPException(status_code=422, detail="The 'email' field is required and must be a non-empty string.")
    try:
        EmailStr.validate(user_in.email)
    except ValidationError:
        raise HTTPException(status_code=422, detail="The 'email' field must be a valid email address.")
    if not isinstance(user_in.username, str) or not user_in.username.strip():
        raise HTTPException(status_code=422, detail="The 'username' field is required and must be a non-empty string.")
    if not isinstance(user_in.password, str) or not user_in.password.strip():
        raise HTTPException(status_code=422, detail="The 'password' field is required and must be a non-empty string.")
    if len(user_in.username) > 50:
        raise HTTPException(status_code=422, detail="The 'username' field must not exceed 50 characters.")
    if len(user_in.password) < 6:
        raise HTTPException(status_code=422, detail="The 'password' field must be at least 6 characters long.")
    if len(user_in.password) > 128:
        raise HTTPException(status_code=422, detail="The 'password' field must not exceed 128 characters.")

@router.post("/login", response_model=AuthResponse)
def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    try:
        validate_login_fields(user_in)
        result = login(db, user_in)
        if not result:
            raise HTTPException(status_code=401, detail="Email not registered or password incorrect.")
        user = result["user"]
        return {
            "id": user.id,
            "user_rol": user.user_rol,
            "access_token": result["access_token"]
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/register", response_model=AuthResponse)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    try:
        validate_register_fields(user_in)
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=hash_password(user_in.password),
            user_rol="customer"
        )
        result = register(db, db_user)
        if not result or not result.get("user"):
            raise HTTPException(status_code=400, detail="User could not be registered.")
        return {
            "id": result["user"].id,
            "user_rol": result["user"].user_rol,
            "access_token": result["access_token"]
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/verify-token")
def verify_token(Authorization: str = Header(...)):
    try:
        token = Authorization.split(" ")[1] if " " in Authorization else Authorization
        result = decode_access_token(token)
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")