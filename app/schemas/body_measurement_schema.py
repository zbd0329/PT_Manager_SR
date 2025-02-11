from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BodyMeasurementBase(BaseModel):
    height: float = Field(..., description="Height in centimeters", ge=0)
    weight: float = Field(..., description="Weight in kilograms", ge=0)
    body_fat: float = Field(..., description="Body fat in kilograms", ge=0)
    muscle_mass: float = Field(..., description="Skeletal muscle mass in kilograms", ge=0)
    measurement_date: datetime = Field(..., description="Date of measurement")

class BodyMeasurementCreate(BodyMeasurementBase):
    member_id: str = Field(..., description="ID of the member")

class BodyMeasurementResponse(BodyMeasurementBase):
    id: str
    body_fat_percentage: float = Field(..., description="Body fat percentage calculated from mass")
    bmi: float = Field(..., description="Body Mass Index")

    class Config:
        from_attributes = True 