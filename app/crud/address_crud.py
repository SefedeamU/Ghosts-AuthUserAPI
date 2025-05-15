from sqlalchemy.orm import Session
from app.models.address_model import Address

def create_address(db: Session, address):
    try:
        db.add(address)
        db.commit()
        db.refresh(address)
        return address
    except Exception:
        db.rollback()
        raise

def get_address_by_id(db: Session, address_id):
    try:
        return db.query(Address).filter(Address.id == address_id).first()
    except Exception:
        db.rollback()
        raise

def get_addresses_by_user_id(db: Session, user_id):
    try:
        return db.query(Address).filter(Address.user_id == user_id).all()
    except Exception:
        db.rollback()
        raise

def update_address_by_id(db: Session, address_id, address_data):
    try:
        address = get_address_by_id(db, address_id)
        if address:
            for key, value in address_data.items():
                setattr(address, key, value)
            db.commit()
            db.refresh(address)
        return address
    except Exception:
        db.rollback()
        raise

def delete_address(db: Session, address_id):
    try:
        address = get_address_by_id(db, address_id)
        if address:
            db.delete(address)
            db.commit()
        return address
    except Exception:
        db.rollback()
        raise