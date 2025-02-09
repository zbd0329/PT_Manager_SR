from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class ExperienceLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

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
    fitness_goal: str = Field(..., description="운동 목표 (예: 체중 감량, 근력 향상)")
    experience_level: ExperienceLevel = Field(..., description="운동 경험 수준 (BEGINNER/INTERMEDIATE/ADVANCED)")
    has_injury: bool = Field(..., description="부상 여부")
    injury_description: Optional[str] = Field(None, description="부상 내용 설명")
    session_duration: int = Field(..., ge=30, le=180, description="PT 세션 시간(분) (30분 단위, 30-180분)")
    preferred_exercises: Optional[str] = Field(None, description="선호하는 운동")
    total_pt_count: int = Field(..., ge=0, description="전체 PT 횟수")
    remaining_pt_count: int = Field(..., ge=0, description="남은 PT 횟수")
    notes: Optional[str] = Field(None, description="메모")

    class Config:
        json_schema_extra = {
            "example": {
                "login_id": "member123",
                "password": "password123",
                "name": "홍길동",
                "gender": "MALE",
                "contact": "010-1234-5678",
                "fitness_goal": "체중 감량",
                "experience_level": "BEGINNER",
                "has_injury": False,
                "injury_description": None,
                "session_duration": 60,
                "preferred_exercises": "요가, 필라테스",
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
    fitness_goal: str
    experience_level: ExperienceLevel
    has_injury: bool
    injury_description: Optional[str] = None
    session_duration: int
    preferred_exercises: Optional[str] = None
    total_pt_count: int = Field(default=0, description="총 PT 등록 횟수")
    remaining_pt_count: int = Field(default=0, description="남은 PT 횟수")
    notes: Optional[str] = None
    sequence_number: int = Field(..., description="회원 순번")
    is_active: bool = Field(default=True, description="활성화 상태")
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "login_id": "member123",
                "name": "홍길동",
                "gender": "MALE",
                "contact": "010-1234-5678",
                "fitness_goal": "체중 감량",
                "experience_level": "BEGINNER",
                "has_injury": False,
                "injury_description": None,
                "session_duration": 60,
                "preferred_exercises": "요가, 필라테스",
                "total_pt_count": 10,
                "remaining_pt_count": 10,
                "notes": "특이사항 없음",
                "sequence_number": 1,
                "is_active": True,
                "created_at": "2024-02-08T12:00:00"
            }
        }