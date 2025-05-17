import os

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.address_model import Address
from app.api.deps import get_db
from app.schemas.address_schema import AddressCreate, AddressOut
from app.crud.address_crud import (
    create_address, delete_address, get_address_by_id,
    get_addresses_by_user_id, update_address_by_id, address_exists_for_user, count_addresses_for_user
)

ALLOWED_COUNTRIES = set(os.getenv("ALLOWED_COUNTRIES", "").split(","))
MAX_ADDRESSES_PER_USER = int(os.getenv("MAX_ADDRESSES_PER_USER", 5))

router = APIRouter()

def validate_address_fields(address: AddressCreate):
    if not isinstance(address.street, str) or not address.street.strip():
        raise HTTPException(status_code=422, detail="The 'street' field is required and must be a non-empty string.")
    if len(address.street) > 100:
        raise HTTPException(status_code=422, detail="The 'street' field must not exceed 100 characters.")

    if not isinstance(address.city, str) or not address.city.strip():
        raise HTTPException(status_code=422, detail="The 'city' field is required and must be a non-empty string.")
    if len(address.city) > 50:
        raise HTTPException(status_code=422, detail="The 'city' field must not exceed 50 characters.")

    if not isinstance(address.state, str) or not address.state.strip():
        raise HTTPException(status_code=422, detail="The 'state' field is required and must be a non-empty string.")
    if len(address.state) > 50:
        raise HTTPException(status_code=422, detail="The 'state' field must not exceed 50 characters.")

    if not isinstance(address.zip_code, str) or not address.zip_code.strip():
        raise HTTPException(status_code=422, detail="The 'zip_code' field is required and must be a non-empty string.")
    if len(address.zip_code) > 20:
        raise HTTPException(status_code=422, detail="The 'zip_code' field must not exceed 20 characters.")
    if not address.zip_code.isalnum():
        raise HTTPException(status_code=422, detail="The 'zip_code' field must be alphanumeric.")

    if not isinstance(address.country, str) or not address.country.strip():
        raise HTTPException(status_code=422, detail="The 'country' field is required and must be a non-empty string.")
    if len(address.country) > 50:
        raise HTTPException(status_code=422, detail="The 'country' field must not exceed 50 characters.")
    if address.country not in ALLOWED_COUNTRIES:
        raise HTTPException(status_code=422, detail=f"The 'country' field must be one of: {', '.join(ALLOWED_COUNTRIES)}.")

@router.post(
    "/",
    response_model=AddressOut,
    summary="Create address",
    description="Create a new address for a user. The user cannot have more than the allowed number of addresses. All fields are required.",
    response_description="The created address object."
)
def post_address(
    address: AddressCreate = Body(
        ...,
        examples={
            "user_id": 1,
            "street": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "USA"
        }
    ),
    db: Session = Depends(get_db)
):
    """
    Create a new address for a user.
    """
    validate_address_fields(address)

    user_id = getattr(address, "user_id", None)
    if not user_id or not isinstance(user_id, int) or user_id <= 0:
        raise HTTPException(status_code=422, detail="The 'user_id' field is required and must be a positive integer.")

    if count_addresses_for_user(db, user_id) >= MAX_ADDRESSES_PER_USER:
        raise HTTPException(status_code=400, detail=f"User cannot have more than {MAX_ADDRESSES_PER_USER} addresses.")

    if address_exists_for_user(db, user_id, address):
        raise HTTPException(status_code=400, detail="This address already exists for the user.")

    try:
        db_address = Address(**address.model_dump())
        created = create_address(db, db_address)
        return created
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except TypeError as e:
        raise HTTPException(status_code=422, detail=f"Invalid data sent: {str(e)}")

@router.get(
    "/{address_id}",
    response_model=AddressOut,
    summary="Get address by ID",
    description="Retrieve an address by its unique address ID."
)
def get_address(address_id: int, db: Session = Depends(get_db)):
    """
    Retrieve an address by its unique address ID.
    """
    if not isinstance(address_id, int) or address_id <= 0:
        raise HTTPException(status_code=422, detail="The 'address_id' parameter must be a positive integer.")
    try:
        address = get_address_by_id(db, address_id)
        if not address:
            raise HTTPException(status_code=404, detail="Address not found.")
        return address
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get(
    "/user/{user_id}",
    response_model=list[AddressOut],
    summary="List addresses by user",
    description="Get all addresses for a specific user by user ID.",
    response_description="A list of address objects."
)
def get_addresses_by_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all addresses for a specific user by user ID.
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise HTTPException(status_code=422, detail="The 'user_id' parameter must be a positive integer.")
    try:
        addresses = get_addresses_by_user_id(db, user_id)
        return addresses
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put(
    "/{address_id}",
    response_model=AddressOut,
    summary="Update address",
    description="Update an existing address by its ID.",
    response_description="The updated address object."
)
def update_address(
    address_id: int,
    address: AddressCreate = Body(
        ...,
        examples={
            "user_id": 1,
            "street": "456 Elm St",
            "city": "Boston",
            "state": "MA",
            "zip_code": "02118",
            "country": "USA"
        }
    ),
    db: Session = Depends(get_db)
):
    """
    Update an existing address by its ID.
    """
    if not isinstance(address_id, int) or address_id <= 0:
        raise HTTPException(status_code=422, detail="The 'address_id' parameter must be a positive integer.")

    validate_address_fields(address)

    try:
        updated_address = update_address_by_id(db, address_id, address.model_dump())
        if not updated_address:
            raise HTTPException(status_code=404, detail="Address not found.")
        return updated_address
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except TypeError as e:
        raise HTTPException(status_code=422, detail=f"Invalid data sent: {str(e)}")

@router.delete(
    "/{address_id}",
    response_model=AddressOut,
    summary="Delete address",
    description="Delete an address by its unique address ID."
)
def delete_one_address(address_id: int, db: Session = Depends(get_db)):
    """
    Delete an address by its unique address ID.
    """
    if not isinstance(address_id, int) or address_id <= 0:
        raise HTTPException(status_code=422, detail="The 'address_id' parameter must be a positive integer.")
    try:
        address = delete_address(db, address_id)
        if not address:
            raise HTTPException(status_code=404, detail="Address not found.")
        return address
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")