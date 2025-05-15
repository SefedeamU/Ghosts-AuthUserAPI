from pydantic import BaseModel, EmailStr, Field
from app.schemas.user_schema import UserOut

    # It will be used to login the user
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

    # It will be used to register a new user
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(..., min_length=6)

class AuthResponse(BaseModel):
    id: int
    user_rol: str
    access_token: str