from sqlalchemy import Column, Integer, Float, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid

class BodyMeasurement(Base):
    __tablename__ = "body_measurements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = Column(String(36), ForeignKey("members.id"), nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    body_fat = Column(Float, nullable=False)  # 체지방량 (kg)
    body_fat_percentage = Column(Float, nullable=False)  # 체지방률 (%)
    muscle_mass = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    measurement_date = Column(Date, nullable=False)

    # Relationship
    member = relationship("Member", back_populates="body_measurements")

    def calculate_bmi(self):
        """BMI 계산"""
        height_in_meters = self.height / 100
        return round(self.weight / (height_in_meters ** 2), 1)

    def calculate_body_fat_percentage(self):
        """체지방률 계산"""
        return round((self.body_fat / self.weight) * 100, 1) 