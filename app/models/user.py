from sqlalchemy import Column, String, Date, Enum
from app.models.base import Base  # 절대 경로로 import
from passlib.context import CryptContext
from enum import Enum as PyEnum
import uuid  # UUID 사용을 위한 추가

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserType(PyEnum):
    MEMBER = "member"
    TRAINER = "trainer"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # UUID 자동 생성
    email = Column(String(100), unique=True, index=True, nullable=False)  # 최대 100자
    name = Column(String(50), nullable=False)  # 최대 50자
    birth_date = Column(Date, nullable=True)  # 생일은 선택 사항
    password = Column(String(255), nullable=False)  # 비밀번호 길이 255
    user_type = Column(Enum(UserType), nullable=False)

    def set_password(self, password: str):
        """ 비밀번호를 해싱하여 저장 """
        self.password = pwd_context.hash(password)  # 비밀번호 해싱

    def verify_password(self, plain_password: str) -> bool:
        """ 입력된 비밀번호가 저장된 해시와 일치하는지 검증 """
        return pwd_context.verify(plain_password, self.password)
