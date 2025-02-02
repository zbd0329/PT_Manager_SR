from sqlalchemy import Column, Integer, String, Date, Enum
from ..database import Base
from passlib.context import CryptContext
import enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserType(enum.Enum):
    MEMBER = "member"
    TRAINER = "trainer"

class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    password_hash = Column(String(100), nullable=False)  # 암호화된 비밀번호 저장 
    user_type = Column(Enum(UserType), nullable=False) 