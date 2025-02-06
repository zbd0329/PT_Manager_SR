from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid
from datetime import datetime
from enum import Enum as PyEnum

class InputSource(PyEnum):
    MEMBER = "MEMBER"
    TRAINER = "TRAINER"

class ExerciseRecord(Base):
    __tablename__ = "exercise_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey('pt_sessions.id', ondelete='CASCADE'), nullable=False)
    exercise_name = Column(String(100), nullable=False)
    duration = Column(Integer, nullable=False)  # 초 단위로 저장
    repetitions = Column(Integer, nullable=False)
    sets = Column(Integer, nullable=False, default=1)  # 세트 수 추가
    body_part = Column(Text, nullable=False)
    input_source = Column(Enum(InputSource), nullable=False, default=InputSource.MEMBER)
    member_id = Column(String(36), ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    trainer_id = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    session = relationship("PTSession", back_populates="exercise_records")
    member = relationship("Member", back_populates="exercise_records")
    trainer = relationship("User", back_populates="exercise_records") 