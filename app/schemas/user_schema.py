from pydantic import BaseModel, EmailStr, validator
from datetime import date
from app.models.user_model import UserType
import uuid
from typing import Optional

class UserBase(BaseModel):
    login_id: str
    name: str
    user_type: UserType

class UserCreate(BaseModel):
    login_id: str
    email: Optional[EmailStr] = None
    name: str
    birth_date: str
    password: str
    user_type: UserType = UserType.MEMBER

    @validator('login_id')
    def validate_login_id(cls, v):
        if len(v) < 4:
            raise ValueError("Login ID must be at least 4 characters long")
        return v

class UserLogin(BaseModel):
    login_id: str
    password: str
    user_type: str

class UserResponse(BaseModel):
    id: str
    login_id: str
    email: Optional[str]
    name: str
    birth_date: date
    user_type: UserType

    class Config:
        from_attributes = True