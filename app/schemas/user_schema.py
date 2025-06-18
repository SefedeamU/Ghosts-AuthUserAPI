from pydantic import BaseModel, EmailStr, Field, ConfigDict, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.schemas.address_schema import AddressOut

class UserUpdate(BaseModel, extra="forbid"):
    nickname: Optional[str] = Field(None, examples=["ghosty"], description="User's nickname.")
    firstname: Optional[str] = Field(None, examples=["john"], description="User's first name.")
    lastname: Optional[str] = Field(None, examples=["doe"], description="User's last name.")
    phone: Optional[str] = Field(None, examples=["+1234567890"], description="User's phone number.")
    address: Optional[str] = Field(None, examples=["123 Main St"], description="User's main address.")
    birthdate: Optional[str] = Field(None, examples=["1990-01-01"], description="User's birthdate (YYYY-MM-DD).")
    gender: Optional[str] = Field(None, examples=["male"], description="User's gender.")
    avatar_url: Optional[str] = Field(None, examples=["https://example.com/avatar.jpg"], description="URL to user's avatar image.")

class UserReplace(BaseModel, extra="forbid"):
    firstname: str = Field(..., examples=["john_doe"], description="User's display name.")
    lastname: str = Field(..., examples=["john_doe"], description="User's display name.")
    nickname: Optional[str] = Field(None, examples=["ghosty"], description="User's nickname.")
    phone: Optional[str] = Field(None, examples=["+1234567890"], description="User's phone number.")
    address: Optional[str] = Field(None, examples=["123 Main St"], description="User's main address.")
    birthdate: Optional[str] = Field(None, examples=["1990-01-01"], description="User's birthdate (YYYY-MM-DD).")
    gender: Optional[str] = Field(None, examples=["male"], description="User's gender.")
    avatar_url: Optional[str] = Field(None, examples=["https://example.com/avatar.jpg"], description="URL to user's avatar image.")

class UserOut(BaseModel):
    id: int = Field(..., examples=[1], description="Unique user ID.")
    email: EmailStr = Field(..., examples=["user@example.com"], description="User's email address.")
    firstname: str = Field(..., examples=["john_doe"], description="User's display name.")
    nickname: Optional[str] = Field(None, examples=["ghosty"], description="User's nickname.")
    lastname: str = Field(..., examples=["john_doe"], description="User's display name.")
    phone: Optional[str] = Field(None, examples=["+1234567890"], description="User's phone number.")
    address: Optional[str] = Field(None, examples=["123 Main St"], description="User's main address.")
    birthdate: Optional[str] = Field(None, examples=["1990-01-01"], description="User's birthdate (YYYY-MM-DD).")
    gender: Optional[str] = Field(None, examples=["male"], description="User's gender.")
    avatar_url: Optional[str] = Field(None, examples=["https://example.com/avatar.jpg"], description="URL to user's avatar image.")
    user_rol: str = Field(..., examples=["customer"], description="User's role in the system.")
    is_active: bool = Field(..., examples=[True], description="Whether the user is active.")
    is_verified: bool = Field(..., examples=[False], description="Whether the user has verified their email.")
    created_at: datetime = Field(..., examples=["2024-01-01T12:00:00Z"], description="User creation timestamp.")
    updated_at: Optional[datetime] = Field(None, examples=["2024-01-02T12:00:00Z"], description="User update timestamp.")
    addresses: List[AddressOut] = Field(default_factory=list, description="List of user's addresses.")
    stripe_customer_id: Optional[str] = Field(None, examples=["cus_N1a2b3c4d5e6f7"], description="Stripe customer ID.")


    model_config = ConfigDict(from_attributes=True)