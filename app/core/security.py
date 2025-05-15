from passlib.context import CryptContext

from datetime import datetime, timedelta, timezone
from jose import ExpiredSignatureError, JWTError, jwt
from app.core.config import settings

# Provide functions to hash and verify passwords using bcrypt.
# It uses the passlib library to handle password hashing and verification.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Function to create a JWT access token.
# It takes a dictionary of data and an optional expiration time in hours.
def create_access_token(data: dict, user_rol: str):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({
        "exp": expire,
        "rol": user_rol
    })
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return {"valid": True, "payload": payload}
    except ExpiredSignatureError:
        return {"valid": False, "error": "Token expired"}
    except JWTError:
        return {"valid": False, "error": "Invalid token"}