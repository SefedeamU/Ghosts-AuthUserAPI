import re
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import EmailStr, ValidationError

from app.api.auth_routes import validate_password
from app.api.deps import get_db
from app.crud.user_crud import delete_user, get_user_by_email, get_user_by_id, get_users, update_user_by_id
from app.schemas.user_schema import UserOut, UserReplace, UserUpdate

router = APIRouter()

def validate_user_id(user_id):
    if not isinstance(user_id, int) or user_id <= 0:
        raise HTTPException(status_code=422, detail="The 'user_id' parameter must be a positive integer.")

def validate_email(email):
    if not isinstance(email, str) or not email.strip():
        raise HTTPException(status_code=422, detail="The 'email' parameter is required and must be a non-empty string.")
    try:
        EmailStr.validate(email)
    except ValidationError:
        raise HTTPException(status_code=422, detail="The 'email' parameter must be a valid email address.")

def validate_update_data(user_data: dict, db: Session, user_id: int):
    if "password" in user_data:
        raise HTTPException(
            status_code=403,
            detail="Password cannot be updated from this endpoint. Use the password reset flow."
        )
    if "email" in user_data:
        validate_email(user_data["email"])
        existing_user = get_user_by_email(db, user_data["email"])
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=409, detail="The 'email' is already in use by another user.")
    if "firstname" in user_data:
        if not isinstance(user_data["firstname"], str) or not user_data["firstname"].strip():
            raise HTTPException(status_code=422, detail="The 'firstname' field is required and must be a non-empty string.")
        if len(user_data["firstname"]) > 50:
            raise HTTPException(status_code=422, detail="The 'firstname' field must not exceed 50 characters.")
    if "lastname" in user_data:
        if not isinstance(user_data["lastname"], str) or not user_data["lastname"].strip():
            raise HTTPException(status_code=422, detail="The 'lastname' field is required and must be a non-empty string.")
        if len(user_data["lastname"]) > 50:
            raise HTTPException(status_code=422, detail="The 'lastname' field must not exceed 50 characters.")
    if "phone" in user_data:
        if not isinstance(user_data["phone"], str) or not user_data["phone"].strip():
            raise HTTPException(status_code=422, detail="The 'phone' field is required and must be a non-empty string.")
        if not re.match(r"^\+\d{7,15}$", user_data["phone"]):
            raise HTTPException(status_code=422, detail="The 'phone' field must be a valid international phone number (e.g., +1234567890).")

@router.get(
    "/",
    response_model=list[UserOut],
    summary="List users",
    description="Get a paginated list of users.",
    response_description="A list of user objects."
)
def list_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of users to skip", examples=0),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of users to return", examples=10)
):
    """
    Retrieve a paginated list of users.
    """
    try:
        result = get_users(db, skip=skip, limit=limit)
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Get user by ID",
    description="Retrieve a user by their unique user ID."
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a user by their unique user ID.
    """
    validate_user_id(user_id)
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get(
    "/email/{email}",
    response_model=UserOut,
    summary="Get user by email",
    description="Retrieve a user by their email address."
)
def get_user_by_email_route(email: str, db: Session = Depends(get_db)):
    """
    Retrieve a user by their email address.
    """
    validate_email(email)
    try:
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.patch(
    "/{user_id}",
    response_model=UserOut,
    summary="Partially update user",
    description="Update one or more fields of a user by user ID.",
    response_description="The updated user object."
)
def partial_update_user(
    user_id: int,
    user_data: UserUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """
    Partially update user information by user ID.
    Only the provided fields will be updated.
    """
    validate_user_id(user_id)
    user_dict = user_data.model_dump(exclude_unset=True)
    if not user_dict:
        raise HTTPException(status_code=422, detail="No data provided for update.")
    validate_update_data(user_dict, db, user_id)
    try:
        user = update_user_by_id(db, user_id, user_dict)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except TypeError as e:
        raise HTTPException(status_code=422, detail=f"Invalid data sent: {str(e)}")

@router.put(
    "/{user_id}",
    response_model=UserOut,
    summary="Replace user",
    description="Replace all user data by user ID. All fields must be provided.",
    response_description="The updated user object."
)
def replace_user(
    user_id: int,
    user_data: UserReplace = Body(...),
    db: Session = Depends(get_db)
):
    """
    Replace all user information by user ID.
    All fields must be provided.
    """
    validate_user_id(user_id)
    user_dict = user_data.model_dump()
    validate_update_data(user_dict, db, user_id)
    try:
        user = update_user_by_id(db, user_id, user_dict)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except TypeError as e:
        raise HTTPException(status_code=422, detail=f"Invalid data sent: {str(e)}")

@router.delete(
    "/{user_id}",
    response_model=UserOut,
    summary="Delete user",
    description="Delete a user by their unique user ID."
)
def remove_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by their unique user ID.
    """
    validate_user_id(user_id)
    try:
        user = delete_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")