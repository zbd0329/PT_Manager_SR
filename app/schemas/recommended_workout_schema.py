from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.recommended_workout import FitnessLevel

class WorkoutDetailBase(BaseModel):
    exercise_name: str = Field(..., description="운동 이름")
    sets: int = Field(..., description="세트 수", gt=0)
    repetitions: int = Field(..., description="반복 횟수", gt=0)
    duration: int = Field(..., description="운동 시간(초)", gt=0)
    rest_time: int = Field(..., description="휴식 시간(초)", gt=0)
    description: Optional[str] = Field(None, description="운동 설명")
    sequence: int = Field(..., description="운동 순서", gt=0)

class WorkoutDetailCreate(WorkoutDetailBase):
    pass

class WorkoutDetailResponse(WorkoutDetailBase):
    id: str
    template_id: str
    created_at: datetime

    class Config:
        orm_mode = True

class WorkoutTemplateBase(BaseModel):
    workout_name: str = Field(..., description="운동 프로그램 이름")
    fitness_level: FitnessLevel = Field(..., description="운동 난이도")
    target_body_part: str = Field(..., description="목표 신체 부위")
    total_duration: int = Field(..., description="총 운동 시간(분)", gt=0)

class WorkoutTemplateCreate(WorkoutTemplateBase):
    member_id: str
    session_id: str
    workout_details: List[WorkoutDetailCreate]

class WorkoutTemplateResponse(WorkoutTemplateBase):
    id: str
    member_id: str
    trainer_id: str
    session_id: str
    created_at: datetime
    updated_at: datetime
    workout_details: List[WorkoutDetailResponse]

    class Config:
        orm_mode = True

class WorkoutTemplateUpdate(BaseModel):
    workout_name: Optional[str] = None
    fitness_level: Optional[FitnessLevel] = None
    target_body_part: Optional[str] = None
    total_duration: Optional[int] = None
    workout_details: Optional[List[WorkoutDetailCreate]] = None 