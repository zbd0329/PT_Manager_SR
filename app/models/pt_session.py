from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid
from datetime import datetime

class PTSession(Base):
    __tablename__ = "pt_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = Column(String(36), ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    trainer_id = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    session_number = Column(Integer, nullable=False)  # PT 회차
    session_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_completed = Column(Boolean, default=False)  # 수업 완료 여부
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    member = relationship("Member", back_populates="pt_sessions")
    trainer = relationship("User", back_populates="pt_sessions")
    exercise_records = relationship("ExerciseRecord", back_populates="session", cascade="all, delete-orphan") 