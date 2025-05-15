from sqlalchemy.orm import Session
from app.models.user_model import User

def get_users(db: Session, skip: int = 0, limit: int = 10):
    try:
        return db.query(User).offset(skip).limit(limit).all()
    except Exception as e:
        db.rollback()
        raise

def get_user_by_id(db: Session, user_id: int):
    try:
        return db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        db.rollback()
        raise

def get_user_by_email(db: Session, email: str):
    try:
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        db.rollback()
        raise

def update_user_by_id(db: Session, user_id: int, user_data: dict):
    try:
        user = get_user_by_id(db, user_id)
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise

def delete_user(db: Session, user_id: int):
    try:
        user = get_user_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
        return user
    except Exception as e:
        db.rollback()
        raise