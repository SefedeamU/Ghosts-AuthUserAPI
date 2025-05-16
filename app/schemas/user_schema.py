from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.address_schema import AddressOut

class UserUpdate(BaseModel, extra="forbid"):
    username: Optional[str] = Field(None, example="john_doe", description="User's display name.")
    phone: Optional[str] = Field(None, example="+1234567890", description="User's phone number.")
    address: Optional[str] = Field(None, example="123 Main St", description="User's main address.")
    birthdate: Optional[str] = Field(None, example="1990-01-01", description="User's birthdate (YYYY-MM-DD).")
    gender: Optional[str] = Field(None, example="male", description="User's gender.")
    avatar_url: Optional[str] = Field(None, example="https://example.com/avatar.jpg", description="URL to user's avatar image.")

class UserOut(BaseModel):
    id: int = Field(..., example=1, description="Unique user ID.")
    email: EmailStr = Field(..., example="user@example.com", description="User's email address.")
    username: str = Field(..., example="john_doe", description="User's display name.")
    phone: Optional[str] = Field(None, example="+1234567890", description="User's phone number.")
    address: Optional[str] = Field(None, example="123 Main St", description="User's main address.")
    birthdate: Optional[str] = Field(None, example="1990-01-01", description="User's birthdate (YYYY-MM-DD).")
    gender: Optional[str] = Field(None, example="male", description="User's gender.")
    avatar_url: Optional[str] = Field(None, example="https://example.com/avatar.jpg", description="URL to user's avatar image.")
    user_rol: str = Field(..., example="customer", description="User's role in the system.")
    is_active: bool = Field(..., example=True, description="Whether the user is active.")
    is_verified: bool = Field(..., example=False, description="Whether the user has verified their email.")
    created_at: datetime = Field(..., example="2024-01-01T12:00:00Z", description="User creation timestamp.")
    updated_at: Optional[datetime] = Field(None, example="2024-01-02T12:00:00Z", description="User update timestamp.")
    addresses: List[AddressOut] = Field(default_factory=list, description="List of user's addresses.")

    class Config:
        from_attributes = True