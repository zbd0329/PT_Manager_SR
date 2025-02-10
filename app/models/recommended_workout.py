from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from app.models import Base
from datetime import datetime

class RecommendedWorkout(Base):
    __tablename__ = "recommended_workouts"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String(36), ForeignKey("members.id"), nullable=False)
    session_id = Column(String(36), ForeignKey("pt_sessions.id"), nullable=False)
    workout_name = Column(String(100), nullable=False)
    total_duration = Column(Integer, nullable=False)  # 분 단위
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정 - 문자열로 참조
    member = relationship("Member", back_populates="recommended_workouts")
    session = relationship("PTSession", back_populates="recommended_workouts")
    exercises = relationship("RecommendedExercise", back_populates="workout", cascade="all, delete-orphan")

class RecommendedExercise(Base):
    __tablename__ = "recommended_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("recommended_workouts.id"), nullable=False)
    exercise_name = Column(String(100), nullable=False)
    sets = Column(Integer, nullable=False)
    repetitions = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)  # 초 단위
    rest_time = Column(Integer, nullable=False)  # 초 단위
    description = Column(Text)
    sequence = Column(Integer, nullable=False)  # 운동 순서

    # 관계 설정
    workout = relationship("RecommendedWorkout", back_populates="exercises")
