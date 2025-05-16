from pydantic import BaseModel, EmailStr, Field

class UserLogin(BaseModel, extra="forbid"):
    email: EmailStr = Field(..., example="user@example.com", description="User's email address.")
    password: str = Field(..., min_length=6, example="yourpassword", description="User's password (6-128 characters).")

class UserRegister(BaseModel, extra="forbid"):
    email: EmailStr = Field(..., example="newuser@example.com", description="User's email address.")
    username: str = Field(..., example="newuser", description="User's display name.")
    password: str = Field(..., min_length=6, example="securepassword", description="User's password (6-128 characters).")

class AuthResponse(BaseModel):
    id: int = Field(..., example=1, description="User ID.")
    user_rol: str = Field(..., example="customer", description="User's role.")
    access_token: str = Field(..., example="jwt.token.here", description="JWT access token.")

class TokenRequest(BaseModel):
    email: str

class TokenVerify(BaseModel):
    token: str
    new_password: str = None 