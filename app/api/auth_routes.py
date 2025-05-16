from fastapi import APIRouter, Depends, Header, HTTPException, Body
from pydantic import EmailStr, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.security import decode_access_token, hash_password
from app.crud.user_crud import get_user_by_email, update_user_by_id
from app.models.user_model import User
from app.schemas.auth_schema import TokenRequest, TokenVerify, UserRegister, UserLogin, AuthResponse
from app.api.deps import get_db
from app.crud.auth_crud import create_action_token, get_valid_action_token, login, mark_action_token_used, register

router = APIRouter()

def validate_login_fields(user_in: UserLogin):
    if not isinstance(user_in.email, str) or not user_in.email.strip():
        raise HTTPException(status_code=422, detail="The 'email' field is required and must be a non-empty string.")
    if not isinstance(user_in.password, str) or not user_in.password.strip():
        raise HTTPException(status_code=422, detail="The 'password' field is required and must be a non-empty string.")

def validate_register_fields(user_in: UserRegister):
    if not isinstance(user_in.email, str) or not user_in.email.strip():
        raise HTTPException(status_code=422, detail="The 'email' field is required and must be a non-empty string.")
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

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    description="Authenticate a user with email and password. Returns an access token if credentials are valid.",
    response_description="Authentication response with user info and access token."
)
def login_user(
    user_in: UserLogin = Body(
        ...,
        example={
            "email": "user@example.com",
            "password": "yourpassword"
        }
    ),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return an access token.
    """
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

@router.post(
    "/register",
    response_model=AuthResponse,
    summary="User registration",
    description="Register a new user with email, username, and password.",
    response_description="Authentication response with user info and access token."
)
def register_user(
    user_in: UserRegister = Body(
        ...,
        example={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepassword"
        }
    ),
    db: Session = Depends(get_db)
):
    """
    Register a new user and return an access token.
    """
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

        token_obj = create_action_token(db, result["user"].id, "verification", expires_minutes=30)
################### Aquí deberías enviar el email con token_obj.token####################################
        return {
            "id": result["user"].id,
            "user_rol": result["user"].user_rol,
            "access_token": result["access_token"],
            "msg": "User registered successfully. Please verify your email."
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post(
    "/verify-token",
    summary="Verify access token",
    description="Verify the validity of a JWT access token.",
    response_description="Decoded token data if valid."
)
def verify_token(
    Authorization: str = Header(..., description="JWT access token in the format: Bearer <token>")
):
    """
    Verify the validity of a JWT access token.
    """
    try:
        token = Authorization.split(" ")[1] if " " in Authorization else Authorization
        result = decode_access_token(token)
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
@router.post(
    "/request-password-reset",
    summary="Request password reset",
    description="Send a password reset email to the user.",
)
def request_password_reset(
    data: TokenRequest,
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    token_obj = create_action_token(db, user.id, "reset", expires_minutes=30)
######################Aquí deberías enviar el email con el token_obj.token#############################
    return {"msg": "Reset password email sent."}

@router.post(
    "/reset-password",
    summary="Reset password",
    description="Allow the user to reset their password using a token.",
)
def reset_password(
    data: TokenVerify,
    db: Session = Depends(get_db)
):
    user_token = get_valid_action_token(db, data.token, "reset")
    if not user_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")
    if not data.new_password or len(data.new_password) < 6:
        raise HTTPException(status_code=422, detail="The 'new_password' field must be at least 6 characters long.")
    mark_action_token_used(db, data.token)
    hashed = hash_password(data.new_password)
    update_user_by_id(db, user_token.user_id, {"hashed_password": hashed})
    return {"msg": "Password reset successfully."}

@router.post(
    "/request-email-verification",
    summary="Request email verification",
    description="Send an email verification request to the user.",
)
def request_email_verification(
    data: TokenRequest,
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    token_obj = create_action_token(db, user.id, "verification", expires_minutes=30)
#################Aquí deberías enviar el email con token_obj.token############
    return {"msg": "Email de verificación enviado."}

@router.post(
    "/confirm-email",
    summary="Confirmar email",
    description="Confirma el email del usuario usando el token recibido.",
)
def confirm_email(
    data: TokenVerify,
    db: Session = Depends(get_db)
):
    user_token = get_valid_action_token(db, data.token, "verification")
    if not user_token:
        raise HTTPException(status_code=400, detail="Token inválido, expirado o ya usado.")
    mark_action_token_used(db, data.token)
    update_user_by_id(db, user_token.user_id, {"is_verified": True})
    return {"msg": "Email confirmado exitosamente."}