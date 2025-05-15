from sqlalchemy.orm import Session
from app.models.user_model import User
from app.schemas.auth_schema import UserLogin, UserRegister
from app.core.security import create_access_token, hash_password, verify_password

def login(db: Session, user_in: UserLogin):
    try:
        db_user = db.query(User).filter(User.email == user_in.email).first()
        if db_user and verify_password(user_in.password, db_user.hashed_password):
            token = create_access_token({"sub": db_user.id}, db_user.user_rol)
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
        token = create_access_token({"sub": db_user.id}, db_user.user_rol)
        return {"user": db_user, "access_token": token}
    except Exception:
        db.rollback()
        raise