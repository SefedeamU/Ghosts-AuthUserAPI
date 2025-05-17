from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import EmailStr, ValidationError

from app.api.deps import get_db
from app.crud.user_crud import delete_user, get_user_by_email, get_user_by_id, get_users, update_user_by_id
from app.schemas.user_schema import UserOut

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
    if "email" in user_data:
        validate_email(user_data["email"])
        existing_user = get_user_by_email(db, user_data["email"])
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=409, detail="The 'email' is already in use by another user.")
    if "username" in user_data:
        if not isinstance(user_data["username"], str) or not user_data["username"].strip():
            raise HTTPException(status_code=422, detail="The 'username' field is required and must be a non-empty string.")
        if len(user_data["username"]) > 50:
            raise HTTPException(status_code=422, detail="The 'username' field must not exceed 50 characters.")
    if "password" in user_data:
        if not isinstance(user_data["password"], str) or not user_data["password"].strip():
            raise HTTPException(status_code=422, detail="The 'password' field is required and must be a non-empty string.")
        if len(user_data["password"]) < 6:
            raise HTTPException(status_code=422, detail="The 'password' field must be at least 6 characters long.")
        if len(user_data["password"]) > 128:
            raise HTTPException(status_code=422, detail="The 'password' field must not exceed 128 characters.")

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

@router.put(
    "/{user_id}",
    response_model=UserOut,
    summary="Update user",
    description="Update user information by user ID.",
    response_description="The updated user object."
)
def update_user(
    user_id: int,
    user_data: dict = Body(..., examples={"email": "new@mail.com", "username": "newuser"}),
    db: Session = Depends(get_db)
):
    """
    Update user information by user ID.
    """
    validate_user_id(user_id)
    validate_update_data(user_data, db, user_id)
    try:
        user = update_user_by_id(db, user_id, user_data)
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
    
    