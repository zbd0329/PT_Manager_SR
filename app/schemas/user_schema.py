from pydantic import BaseModel, EmailStr, validator, Field
from datetime import date
from app.models.user_model import UserType
import uuid
from typing import Optional

class UserBase(BaseModel):
    login_id: str
    name: str
    user_type: UserType

class UserCreate(BaseModel):
    login_id: str = Field(..., min_length=4, max_length=50, description="로그인 ID (4-50자)")
    email: Optional[EmailStr] = Field(None, description="이메일 (선택사항)")
    name: str = Field(..., min_length=2, max_length=50, description="이름 (2-50자)")
    birth_date: date = Field(..., description="생년월일 (YYYY-MM-DD)")
    password: str = Field(..., min_length=8, max_length=100, description="비밀번호 (8자 이상)")
    user_type: UserType = Field(UserType.MEMBER, description="사용자 유형 (MEMBER 또는 TRAINER)")

    @validator('login_id')
    def validate_login_id(cls, v):
        # 알파벳과 숫자만 허용
        cleaned_id = ''.join(char for char in v if char.isalnum())
        if len(cleaned_id) < 4:
            raise ValueError("아이디는 최소 4자 이상의 영문자와 숫자만 사용 가능합니다")
        return cleaned_id

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다")
        return v

    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v > date.today():
            raise ValueError("생년월일은 오늘 이후의 날짜일 수 없습니다")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "login_id": "trainer123",
                "email": "trainer@example.com",
                "name": "홍길동",
                "birth_date": "1990-01-01",
                "password": "password123",
                "user_type": "TRAINER"
            }
        }

class UserLogin(BaseModel):
    login_id: str = Field(..., description="로그인 ID")
    password: str = Field(..., description="비밀번호")
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