from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid
from datetime import datetime

class UserMember(Base):
    __tablename__ = "users_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trainer_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    member_id = Column(String(36), ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    trainer = relationship("User", back_populates="trainer_members", overlaps="members")
    member = relationship("Member", back_populates="user_members", overlaps="trainers") 