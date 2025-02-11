from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.body_measurement_schema import BodyMeasurementCreate, BodyMeasurementResponse
from app.models.body_measurement_model import BodyMeasurement
from app.core.security import verify_trainer

router = APIRouter(tags=["body-measurement"])

templates = Jinja2Templates(directory="app/templates")

@router.get("/trainer/body-measurement", response_class=HTMLResponse)
async def render_body_measurement_page(request: Request, current_user: dict = Depends(verify_trainer)):
    """회원 신체계측 페이지를 렌더링합니다."""
    return templates.TemplateResponse(
        "trainer/body_measurement.html",
        {"request": request}
    )

@router.post("/api/v1/measurements", response_model=BodyMeasurementResponse)
async def create_measurement(
    measurement: BodyMeasurementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """신체 계측 정보를 저장합니다."""
    db_measurement = BodyMeasurement(
        member_id=measurement.member_id,
        height=measurement.height,
        weight=measurement.weight,
        body_fat=measurement.body_fat,  # kg 단위로 저장
        muscle_mass=measurement.muscle_mass,
        measurement_date=measurement.measurement_date
    )
    
    # BMI와 체지방률 계산
    db_measurement.bmi = db_measurement.calculate_bmi()
    db_measurement.body_fat_percentage = db_measurement.calculate_body_fat_percentage()
    
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

@router.get("/api/v1/measurements/{member_id}", response_model=List[BodyMeasurementResponse])
async def get_measurements(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """회원의 신체 계측 기록을 조회합니다."""
    measurements = db.query(BodyMeasurement)\
        .filter(BodyMeasurement.member_id == member_id)\
        .order_by(BodyMeasurement.measurement_date.desc())\
        .all()
    return measurements

@router.delete("/api/v1/measurements/{measurement_id}")
async def delete_measurement(
    measurement_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """신체 계측 기록을 삭제합니다."""
    measurement = db.query(BodyMeasurement).filter(BodyMeasurement.id == measurement_id).first()
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    
    db.delete(measurement)
    db.commit()
    return {"message": "Measurement deleted successfully"} 