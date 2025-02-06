from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class MemberBase(BaseModel):
    """기본 회원 정보 스키마"""
    login_id: str = Field(..., min_length=4, description="로그인 ID")
    name: str = Field(..., min_length=2, description="회원 이름")
    gender: Gender = Field(..., description="성별 (MALE/FEMALE)")
    contact: str = Field(..., description="연락처")
    notes: Optional[str] = Field(None, description="특이사항")

class MemberCreate(BaseModel):
    """회원 생성 스키마"""
    login_id: str = Field(..., min_length=4, description="로그인 ID")
    password: str = Field(..., min_length=6, description="비밀번호")
    name: str = Field(..., min_length=2, description="회원 이름")
    gender: Gender = Field(..., description="성별 (MALE/FEMALE)")
    contact: str = Field(..., description="연락처")
    total_pt_count: int = Field(default=0, ge=0, description="총 PT 등록 횟수")
    remaining_pt_count: int = Field(default=0, ge=0, description="남은 PT 횟수")
    notes: Optional[str] = Field(default=None, description="특이사항")

    class Config:
        json_schema_extra = {
            "example": {
                "login_id": "member123",
                "password": "password123",
                "name": "홍길동",
                "gender": "MALE",
                "contact": "010-1234-5678",
                "total_pt_count": 10,
                "remaining_pt_count": 10,
                "notes": "특이사항 없음"
            }
        }

class MemberUpdate(BaseModel):
    """회원 정보 수정 스키마"""
    name: Optional[str] = Field(None, min_length=2, description="회원 이름")
    gender: Optional[Gender] = Field(None, description="성별 (MALE/FEMALE)")
    contact: Optional[str] = Field(None, description="연락처")
    total_pt_count: Optional[int] = Field(None, ge=0, description="총 PT 등록 횟수")
    remaining_pt_count: Optional[int] = Field(None, ge=0, description="남은 PT 횟수")
    notes: Optional[str] = Field(None, description="특이사항")
    password: Optional[str] = Field(None, min_length=6, description="비밀번호")

class MemberLogin(BaseModel):
    """회원 로그인 스키마"""
    login_id: str = Field(..., description="로그인 ID")
    password: str = Field(..., description="비밀번호")

class MemberResponse(BaseModel):
    """회원 정보 응답 스키마"""
    id: str
    login_id: str
    name: str
    gender: Gender
    contact: str
    total_pt_count: int = Field(default=0, description="총 PT 등록 횟수")
    remaining_pt_count: int = Field(default=0, description="남은 PT 횟수")
    notes: Optional[str] = None
    sequence_number: int = Field(..., description="회원 순번")
    is_active: bool = Field(default=True, description="활성화 상태")
    created_at: datetime

    class Config:
        from_attributes = True