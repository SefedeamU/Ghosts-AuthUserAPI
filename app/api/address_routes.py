from app.models.address_model import Address
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.address_crud import create_address, delete_address, get_address_by_id, get_addresses_by_user_id, update_address_by_id
from app.schemas.address_schema import AddressCreate, AddressOut


router = APIRouter()

@router.post("/", response_model=AddressOut)
def post_address(address: AddressCreate, db: Session = Depends(get_db)):
    db_address = Address(**address.model_dump())
    created = create_address(db, db_address)
    return  created

@router.get("/{address_id}", response_model=AddressOut)
def get_address(address_id: int, db: Session = Depends(get_db)):
    address = get_address_by_id(db, address_id)
    return address

@router.get("/user/{user_id}", response_model=list[AddressOut])
def get_addresses_by_user(user_id: int, db: Session = Depends(get_db)):
    addresses = get_addresses_by_user_id(db, user_id)
    return addresses

@router.put("/{address_id}", response_model=AddressOut)
def update_address(address_id: int, address: AddressCreate, db: Session = Depends(get_db)):
    updated_address = update_address_by_id(db, address_id, address.model_dump())
    return updated_address

@router.delete("/{address_id}", response_model=AddressOut)
def delete_one_address(address_id: int, db: Session = Depends(get_db)):
    address = delete_address(db, address_id)
    return address