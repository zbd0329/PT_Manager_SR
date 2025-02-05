from pydantic import BaseModel, validator, Field
from typing import Optional
from datetime import datetime
from app.models.member_model import GenderEnum

class MemberCreate(BaseModel):
    login_id: str
    name: str
    gender: GenderEnum
    contact: str
    pt_count: int = 0
    notes: Optional[str] = None
    password: str

    @validator('contact')
    def validate_contact(cls, v):
        # 숫자와 -만 허용
        if not all(c.isdigit() or c == '-' for c in v):
            raise ValueError('연락처는 숫자와 하이픈(-)만 포함할 수 있습니다')
        return v

    @validator('login_id')
    def validate_login_id(cls, v):
        if len(v) < 4:
            raise ValueError('로그인 ID는 최소 4자 이상이어야 합니다')
        return v

class MemberResponse(BaseModel):
    id: str
    login_id: str
    name: str
    gender: GenderEnum
    contact: str
    pt_count: int
    notes: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MemberUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    contact: Optional[str] = None
    pt_count: Optional[int] = None
    notes: Optional[str] = None
    password: Optional[str] = None

    @validator('contact')
    def validate_contact(cls, v):
        if v is not None:
            if not all(c.isdigit() or c == '-' for c in v):
                raise ValueError('연락처는 숫자와 하이픈(-)만 포함할 수 있습니다')
        return v

class MemberLogin(BaseModel):
    login_id: str = Field(..., description="로그인 ID")
    password: str = Field(..., description="비밀번호")