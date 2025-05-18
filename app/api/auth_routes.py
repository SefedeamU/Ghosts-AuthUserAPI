from datetime import datetime, timezone
import re
import token
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import decode_access_token, hash_password, verify_password
from app.crud.user_crud import get_user_by_email, get_user_by_id, update_user_by_id
from app.models.auth_model import PasswordRestoreToken
from app.models.user_model import User
from app.schemas.auth_schema import TokenRequest, TokenReset, TokenVerify, UndoPasswordChangeRequest, UserRegister, UserLogin, AuthResponse
from app.api.deps import get_db
from app.crud.auth_crud import create_action_token, get_valid_action_token, login, mark_action_token_used, register
from app.utils.email_utils import load_template, send_email

router = APIRouter()
bearer_scheme = HTTPBearer()

def validate_password(password: str):
    if not isinstance(password, str) or not password.strip():
        raise HTTPException(status_code=400, detail="The 'password' field is required and must be a non-empty string.")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="The 'password' field must be at least 6 characters long.")
    if len(password) > 128:
        raise HTTPException(status_code=400, detail="The 'password' field must not exceed 128 characters.")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="The 'password' must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="The 'password' must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        raise HTTPException(status_code=400, detail="The 'password' must contain at least one digit.")

def validate_register_fields(user_in: UserRegister):
    if not isinstance(user_in.email, str) or not user_in.email.strip():
        raise HTTPException(status_code=400, detail="The 'email' field is required and must be a non-empty string.")
    if not isinstance(user_in.firstname, str) or not user_in.firstname.strip():
        raise HTTPException(status_code=400, detail="The 'firstname' field is required and must be a non-empty string.")
    if len(user_in.firstname) > 50:
        raise HTTPException(status_code=400, detail="The 'firstname' field must not exceed 50 characters.")
    if not isinstance(user_in.lastname, str) or not user_in.lastname.strip():
        raise HTTPException(status_code=400, detail="The 'lastname' field is required and must be a non-empty string.")
    if len(user_in.lastname) > 50:
        raise HTTPException(status_code=400, detail="The 'lastname' field must not exceed 50 characters.")
    if not isinstance(user_in.phone, str) or not user_in.phone.strip():
        raise HTTPException(status_code=400, detail="The 'phone' field is required and must be a non-empty string.")
    if not re.match(r"^\+\d{7,15}$", user_in.phone):
        raise HTTPException(status_code=400, detail="The 'phone' field must be a valid international phone number (e.g., +1234567890).")
    validate_password(user_in.password)

def validate_login_fields(user_in: UserLogin):
    if not isinstance(user_in.email, str) or not user_in.email.strip():
        raise HTTPException(status_code=400, detail="The 'email' field is required and must be a non-empty string.")
    validate_password(user_in.password)
    
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
        examples={
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
        examples={
            "email": "newuser@example.com",
            "firstname": "John",
            "lastname": "Doe",
            "phone": "+1234567890",
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
        existing_user = get_user_by_email(db, user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="The email is already registered.")

        db_user = User(
            email=user_in.email,
            firstname=user_in.firstname,
            lastname=user_in.lastname,
            phone=user_in.phone,
            hashed_password=hash_password(user_in.password),
            user_rol="customer"
        )
        result = register(db, db_user)
        if not result or not result.get("user"):
            raise HTTPException(status_code=400, detail="User could not be registered.")

        token_obj = create_action_token(db, result["user"].id, "verification", expires_minutes=30)
        confirmation_link = f"https://tu-frontend.com/confirm-email?token={token_obj.token}"

        email_body = load_template(
            "welcome.html",
            {
                "username": f"{result["user"].firstname} {result["user"].lastname}",
                "confirmation_link": confirmation_link
            }
        )
        send_email(
            to_email=result["user"].email,
            subject="Confirm your email for Ghosts-API",
            body=email_body
        )

        return {
            "id": result["user"].id,
            "user_rol": result["user"].user_rol,
            "access_token": result["access_token"],
            "msg": "User registered successfully. Please verify your email."
        }
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

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
        raise HTTPException(status_code=404, detail="User not found.")
    if getattr(user, "is_verified", False):
        raise HTTPException(status_code=400, detail="User is already verified.")
    token_obj = create_action_token(db, user.id, "verification", expires_minutes=30)

    confirmation_link = f"https://tu-frontend.com/confirm-email?token={token_obj.token}"
    email_body = load_template(
            "welcome.html",
            {
                "username": f"{user.firstname} {user.lastname}",
                "confirmation_link": confirmation_link
            }
        )
    send_email(
        to_email=user.email,
        subject="Confirm your email for Ghosts-API",
        body=email_body
    )
    return {"msg": "Verification email sent."}

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

    reset_link = f"https://tu-frontend.com/reset-password?token={token_obj.token}"
    email_body = load_template(
        "reset_password.html",
        {
            "username": f"{user.firstname} {user.lastname}",
            "reset_link": reset_link
        }
    )
    send_email(
        to_email=user.email,
        subject="Reset your password for Ghosts-API",
        body=email_body
    )
    return {"msg": "Reset password email sent."}

@router.post(
    "/confirm-email",
    summary="Confirm email",
    description="Confirm the user's email using the received token.",
)
def confirm_email(
    data: TokenVerify,
    db: Session = Depends(get_db)
):
    user_token = get_valid_action_token(db, data.token, "verification")
    if not user_token:
        raise HTTPException(status_code=400, detail="Invalid, expired or already used token.")
    mark_action_token_used(db, data.token)
    update_user_by_id(db, user_token.user_id, {"is_verified": True})
    return {"msg": "Email confirmado exitosamente."}

@router.post(
    "/reset-password",
    summary="Reset password",
    description="Allow the user to reset their password using a token.",
)
def reset_password(
    data: TokenReset,
    db: Session = Depends(get_db)
):
    user_token = get_valid_action_token(db, data.token, "reset")
    if not user_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")
    validate_password(data.new_password)
    user = get_user_by_id(db, user_token.user_id)
    if user and verify_password(data.new_password, user.hashed_password):
        raise HTTPException(status_code=422, detail="The new password must be different from the previous one.")

    restore_token = create_action_token(
        db,
        user_token.user_id,
        "restore",
        expires_minutes=30,
        extra_payload={"old_hashed_password": user.hashed_password},
        use_restore_table=True,
        old_hashed_password=user.hashed_password
    )

    mark_action_token_used(db, data.token)
    hashed = hash_password(data.new_password)
    update_user_by_id(db, user_token.user_id, {"hashed_password": hashed})

    undo_link = f"https://tu-frontend.com/undo-password-change?token={restore_token.token}"
    email_body = load_template(
        "password_changed.html",
        {
            "username": f"{user.firstname} {user.lastname}",
            "support_email": "soporte@your-domain.com",
            "undo_link": undo_link
        }
    )
    send_email(
        to_email=user.email,
        subject="Your password has been changed for Ghosts-API",
        body=email_body
    )

    return {"msg": "Password reset successfully."}

@router.post("/undo-password-change")
def undo_password_change(
    data: UndoPasswordChangeRequest,
    db: Session = Depends(get_db)
):
    restore_token = db.query(PasswordRestoreToken).filter_by(token=data.token, used=False).first()
    if not restore_token or restore_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired token.")
    update_user_by_id(db, restore_token.user_id, {"hashed_password": restore_token.old_hashed_password})
    restore_token.used = True
    db.commit()
    return {"msg": "Your password has been restored. If no fuiste tú, cambia tu contraseña inmediatamente."}

@router.post(
    "/verify-token",
    summary="Verify access token",
    description="Verify the validity of a JWT access token.",
    response_description="Decoded token data if valid."
)
def verify_token(
    data: TokenVerify
):
    """
    Verify the validity of a JWT access token.
    """
    try:
        result = decode_access_token(data.token)
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")