from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

#Instantiate the declarative base class
Base = declarative_base()

# Define the User class that maps to the users table in the database
class User(Base):
    __tablename__ = "users"

    # Define the columns for the users table in the database
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    username = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    user_rol = Column(String, default="customer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    address = Column(String, nullable=True)
    birthdate = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)