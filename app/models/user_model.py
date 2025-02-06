from sqlalchemy import Column, String, Date, Enum, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base
from passlib.context import CryptContext
from enum import Enum as PyEnum
import uuid
from datetime import datetime

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserType(PyEnum):
    MEMBER = "member"
    TRAINER = "trainer"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    login_id = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    name = Column(String(50), nullable=False)
    birth_date = Column(Date, nullable=True)
    password = Column(String(255), nullable=False)
    user_type = Column(Enum(UserType), nullable=False)

    # M:N 관계 설정
    members = relationship("Member", secondary="users_members", back_populates="trainers")
    # PT 세션 관계 설정
    pt_sessions = relationship("PTSession", back_populates="trainer")

    def set_password(self, password: str):
        """ 비밀번호를 해싱하여 저장 """
        self.password = pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:
        """ 입력된 비밀번호가 저장된 해시와 일치하는지 검증 """
        return pwd_context.verify(plain_password, self.password)