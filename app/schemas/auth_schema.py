from pydantic import BaseModel, EmailStr, Field

class UserLogin(BaseModel, extra="forbid"):
    email: EmailStr = Field(..., examples=["user@example.com"], description="User's email address.")
    password: str = Field(..., examples=["yourpassword"], description="User's password (6-128 characters).")

class UserRegister(BaseModel, extra="forbid"):
    email: EmailStr = Field(..., examples=["newuser@example.com"], description="User's email address.")
    firstname: str = Field(..., examples=["john"], description="User's first name.")
    lastname: str = Field(..., examples=["doe"], description="User's last name.")
    password: str = Field(..., examples=["securepassword"], description="User's password (6-128 characters).")
    phone: str = Field(..., examples=["+1234567890"], description="User's phone number.")

class AuthResponse(BaseModel):
    id: int = Field(..., examples=[1], description="User ID.")
    user_rol: str = Field(..., examples=["customer"], description="User's role.")
    access_token: str = Field(..., examples=["jwt.token.here"], description="JWT access token.")

class TokenRequest(BaseModel):
    email: str

class TokenReset(BaseModel):
    token: str
    new_password: str = None 

class TokenVerify(BaseModel):
    token: str

class UndoPasswordChangeRequest(BaseModel):
    token: str