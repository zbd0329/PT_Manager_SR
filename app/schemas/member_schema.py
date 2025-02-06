from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class Gender(str, Enum):
    M = "M"
    F = "F"

class MemberBase(BaseModel):
    login_id: str = Field(..., min_length=4, description="로그인 ID")
    name: str = Field(..., min_length=2, description="회원 이름")
    gender: Gender = Field(..., description="성별 (M/F)")
    contact: str = Field(..., description="연락처")
    pt_count: int = Field(default=0, ge=0, description="PT 횟수")
    notes: Optional[str] = Field(None, description="특이사항")

class MemberCreate(MemberBase):
    password: str = Field(..., min_length=6, description="비밀번호")

class MemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, description="회원 이름")
    gender: Optional[Gender] = Field(None, description="성별 (M/F)")
    contact: Optional[str] = Field(None, description="연락처")
    pt_count: Optional[int] = Field(None, ge=0, description="PT 횟수")
    notes: Optional[str] = Field(None, description="특이사항")
    password: Optional[str] = Field(None, min_length=6, description="비밀번호")

class MemberLogin(BaseModel):
    login_id: str = Field(..., description="로그인 ID")
    password: str = Field(..., description="비밀번호")

class MemberResponse(MemberBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True