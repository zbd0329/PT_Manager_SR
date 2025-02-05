from sqlalchemy import Column, String, Date, Enum
from app.models.base import Base
from passlib.context import CryptContext
from enum import Enum as PyEnum
import uuid

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserType(PyEnum):
    MEMBER = "member"
    TRAINER = "trainer"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, nullable=False, default=str(uuid.uuid4()))
    email = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(50), nullable=False)
    birth_date = Column(Date, nullable=True)
    password = Column(String(255), nullable=False)
    user_type = Column(Enum(UserType), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())

    def set_password(self, password: str):
        """ 비밀번호를 해싱하여 저장 """
        self.password = pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:
        """ 입력된 비밀번호가 저장된 해시와 일치하는지 검증 """
        return pwd_context.verify(plain_password, self.password) 