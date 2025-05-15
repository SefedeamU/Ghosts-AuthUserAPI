from app.models.address_model import Address
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import get_db
from app.crud.address_crud import create_address, delete_address, get_address_by_id, get_addresses_by_user_id, update_address_by_id
from app.schemas.address_schema import AddressCreate, AddressOut

router = APIRouter()

@router.post("/", response_model=AddressOut)
def post_address(address: AddressCreate, db: Session = Depends(get_db)):
    try:
        db_address = Address(**address.model_dump())
        created = create_address(db, db_address)
        return created
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

@router.get("/{address_id}", response_model=AddressOut)
def get_address(address_id: int, db: Session = Depends(get_db)):
    try:
        address = get_address_by_id(db, address_id)
        return address
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

@router.get("/user/{user_id}", response_model=list[AddressOut])
def get_addresses_by_user(user_id: int, db: Session = Depends(get_db)):
    try:
        addresses = get_addresses_by_user_id(db, user_id)
        return addresses
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

@router.put("/{address_id}", response_model=AddressOut)
def update_address(address_id: int, address: AddressCreate, db: Session = Depends(get_db)):
    try:
        updated_address = update_address_by_id(db, address_id, address.model_dump())
        return updated_address
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

@router.delete("/{address_id}", response_model=AddressOut)
def delete_one_address(address_id: int, db: Session = Depends(get_db)):
    try:
        address = delete_address(db, address_id)
        return address
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")