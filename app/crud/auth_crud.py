from datetime import datetime, timedelta, timezone
import secrets
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_model import PasswordRestoreToken, ActionToken
from app.models.user_model import User
from app.schemas.auth_schema import UserLogin
from app.core.security import create_access_token, verify_password

def login(db: Session, user_in: UserLogin):
    try:
        db_user = db.query(User).filter(User.email == user_in.email).first()
        if db_user and verify_password(user_in.password, db_user.hashed_password):
            token = create_access_token({"sub": str(db_user.id)}, db_user.user_rol)
            return {"user": db_user, "access_token": token}
        return None
    except Exception:
        db.rollback()
        raise

def register(db: Session, db_user):
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        token = create_access_token({"sub": str(db_user.id)}, db_user.user_rol)
        return {"user": db_user, "access_token": token}
    except Exception:
        db.rollback()
        raise

def get_valid_action_token(db: Session, token: str, type_: str):
    user_token = db.query(ActionToken).filter(
        ActionToken.token == token,
        ActionToken.type == type_,
        ActionToken.used == False,
        ActionToken.expires_at > datetime.now(timezone.utc)
    ).first()
    if not user_token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != type_:
            return None
        return user_token
    except (ExpiredSignatureError, JWTError):
        return None
    except Exception:
        return None

def mark_action_token_used(db: Session, token: str):
    user_token = db.query(ActionToken).filter(ActionToken.token == token).first()
    if user_token:
        user_token.used = True
        db.commit()

def create_action_token(
    db: Session,
    user_id: int,
    type_: str,
    expires_minutes: int = 30,
    extra_payload: dict = None,
    use_restore_table: bool = False,
    old_hashed_password: str = None
):
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {
        "sub": str(user_id),
        "type": type_,
        "exp": expire
    }
    if extra_payload:
        payload.update(extra_payload)
    token = create_access_token(payload, user_rol=None, expires_delta=timedelta(minutes=expires_minutes))

    if use_restore_table:
        restore_token = PasswordRestoreToken(
            user_id=user_id,
            old_hashed_password=old_hashed_password,
            token=token,
            expires_at=expire,
            used=False
        )
        db.add(restore_token)
        db.commit()
        db.refresh(restore_token)
        return restore_token
    else:
        user_token = ActionToken(
            user_id=user_id,
            token=token,
            type=type_,
            expires_at=expire,
            used=False
        )
        db.add(user_token)
        db.commit()
        db.refresh(user_token)
        return user_token