from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    pt_sessions = relationship("PTSession", back_populates="member")
    exercise_records = relationship("ExerciseRecord", back_populates="member")
    recommended_workouts = relationship("RecommendedWorkout", back_populates="member")
    user_members = relationship("UserMember", back_populates="member") 