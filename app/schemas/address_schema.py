from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AddressBase(BaseModel, extra="forbid"):
    street: str = Field(..., example="123 Main St", description="Street name and number.")
    city: str = Field(..., example="New York", description="City name.")
    state: str = Field(..., example="NY", description="State or province.")
    zip_code: str = Field(..., example="10001", description="Postal or ZIP code (alphanumeric, max 20 chars).")
    country: str = Field(..., example="USA", description="Country name (must be allowed).")

class AddressCreate(AddressBase, extra="forbid"):
    user_id: int = Field(..., example=1, description="ID of the user who owns this address.")

class AddressOut(AddressBase):
    id: int = Field(..., example=10, description="Unique address ID.")

    class Config:
        from_attributes = True