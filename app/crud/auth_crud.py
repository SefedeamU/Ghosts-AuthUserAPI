from datetime import datetime, timedelta, timezone
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_model import UserToken
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

def create_action_token(db: Session, user_id: int, type_: str, expires_minutes: int = 30):
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {
        "sub": str(user_id),
        "type": type_,
        "exp": expire
    }
    token = create_access_token(payload, user_rol=None, expires_delta=timedelta(minutes=expires_minutes))
    user_token = UserToken(
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

def get_valid_action_token(db: Session, token: str, type_: str):
    user_token = db.query(UserToken).filter(
        UserToken.token == token,
        UserToken.type == type_,
        UserToken.used == False,
        UserToken.expires_at > datetime.now(timezone.utc)
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

def mark_action_token_used(db: Session, token: str):
    user_token = db.query(UserToken).filter(UserToken.token == token).first()
    if user_token:
        user_token.used = True
        db.commit()