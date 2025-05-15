from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class AddressBase(BaseModel, extra="forbid"):
    street: str
    city: str
    state: str
    zip_code: str
    country: str

class AddressCreate(AddressBase, extra="forbid"):
    pass

class AddressOut(AddressBase):
    id: int

    class Config:
        from_attributes = True
