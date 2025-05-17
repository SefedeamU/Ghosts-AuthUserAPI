from pydantic import BaseModel, Field, ConfigDict

class AddressBase(BaseModel, extra="forbid"):
    street: str = Field(..., examples="123 Main St", description="Street name and number.")
    city: str = Field(..., examples="New York", description="City name.")
    state: str = Field(..., examples="NY", description="State or province.")
    zip_code: str = Field(..., examples="10001", description="Postal or ZIP code (alphanumeric, max 20 chars).")
    country: str = Field(..., examples="USA", description="Country name (must be allowed).")

class AddressCreate(AddressBase, extra="forbid"):
    user_id: int = Field(..., examples=1, description="ID of the user who owns this address.")

class AddressOut(AddressBase):
    id: int = Field(..., examples=10, description="Unique address ID.")

    model_config = ConfigDict(from_attributes=True)