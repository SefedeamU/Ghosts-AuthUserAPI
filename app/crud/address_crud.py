from sqlalchemy.orm import Session

from app.models.address_model import Address

def create_address(db: Session, address):
    db.add(address)
    db.commit()
    db.refresh(address)
    return address

def get_address_by_id(db: Session, address_id):
    return db.query(Address).filter(Address.id == address_id).first()

def get_addresses_by_user_id(db: Session, user_id):
    return db.query(Address).filter(Address.user_id == user_id).all()

def update_address_by_id(db: Session, address_id, address_data):
    address = get_address_by_id(db, address_id)
    if address:
        for key, value in address_data.items():
            setattr(address, key, value)
        db.commit()
        db.refresh(address)
    return address

def delete_address(db: Session, address_id):
    address = get_address_by_id(db, address_id)
    if address:
        db.delete(address)
        db.commit()
    return address