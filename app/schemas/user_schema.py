from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

    # It will be used to login the user
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

    # It will be used to register a new user
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(..., min_length=6)

    # It will be used to update the user information
class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    birthdate: Optional[str] = None
    gender: Optional[str] = None
    avatar_url: Optional[str] = None

    #Child from BaseModel
    # It will be used to send the user information to the client
class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    phone: Optional[str] = None
    address: Optional[str] = None
    birthdate: Optional[str] = None
    gender: Optional[str] = None
    avatar_url: Optional[str] = None
    user_rol: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True  # Allow convert SQLAlchemy models to Pydantic models