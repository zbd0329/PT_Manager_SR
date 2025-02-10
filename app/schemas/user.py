from pydantic import BaseModel, EmailStr  # EmailStr 올바르게 가져오기
from datetime import date
from app.models.user import UserType  # Enum 타입 불러오기
import uuid
from enum import Enum

class UserType(str, Enum):
    MEMBER = "member"
    TRAINER = "trainer"

class UserBase(BaseModel):
    email: str
    name: str
    user_type: UserType

# class UserCreate(UserBase):
#     id: str
#     birth_date: date
#     password: constr(min_length=4)  # 최소 8자 이상

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    birth_date: str  # 문자열로 받기
    password: str
    user_type: UserType = UserType.MEMBER  # 기본값 설정

class UserLogin(BaseModel):
    id: str
    password: str
    user_type: UserType

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    birth_date: date  # date 타입으로 변경
    user_type: UserType

    class Config:
        from_attributes = True 