from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from passlib.context import CryptContext
from enum import Enum as PyEnum
import uuid
from datetime import datetime

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Gender(PyEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class Member(Base):
    __tablename__ = "members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sequence_number = Column(Integer, nullable=False, unique=True)  # 회원 순번
    login_id = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    gender = Column(Enum(Gender), nullable=True)
    contact = Column(String(20), nullable=False)
    total_pt_count = Column(Integer, default=0)  # 총 PT 등록 횟수
    remaining_pt_count = Column(Integer, default=0)  # 남은 PT 횟수
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정
    trainers = relationship("User", secondary="users_members", back_populates="members", overlaps="user_members,trainer")
    pt_sessions = relationship("PTSession", back_populates="member", cascade="all, delete-orphan")
    user_members = relationship("UserMember", back_populates="member", overlaps="trainers")
    exercise_records = relationship("ExerciseRecord", back_populates="member", cascade="all, delete-orphan")

    def set_password(self, password: str):
        """ 비밀번호를 해싱하여 저장 """
        self.password = pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:
        """ 입력된 비밀번호가 저장된 해시와 일치하는지 검증 """
        return pwd_context.verify(plain_password, self.password)