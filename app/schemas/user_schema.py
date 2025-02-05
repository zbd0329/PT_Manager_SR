from pydantic import BaseModel, EmailStr
from datetime import date
from app.models.user_model import UserType
import uuid
from enum import Enum

class UserBase(BaseModel):
    email: str
    name: str
    user_type: UserType

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    birth_date: str  # 문자열로 받기
    password: str
    user_type: UserType = UserType.MEMBER  # 기본값 설정

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    user_type: str  # UserType Enum 대신 문자열로 받음

    @property
    def user_type_enum(self) -> UserType:
        """문자열로 받은 user_type을 UserType Enum으로 변환"""
        return UserType(self.user_type)

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    birth_date: date  # date 타입으로 변경
    user_type: UserType

    class Config:
        from_attributes = True 