from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, Enum, ForeignKey
from app.models.base import Base
import uuid
from datetime import datetime
import enum

class GenderEnum(str, enum.Enum):
    MALE = "M"
    FEMALE = "F"

class Member(Base):
    __tablename__ = "members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    login_id = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    contact = Column(String(20), nullable=False)
    pt_count = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    trainer_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)