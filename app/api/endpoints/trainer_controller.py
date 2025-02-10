from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.security import verify_trainer
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.member_model import Member
from app.models.users_members import UserMember

router = APIRouter(prefix="/trainer", tags=["trainer"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/exercise-management", response_class=HTMLResponse)
async def exercise_management_page(request: Request, current_user: dict = Depends(verify_trainer)):
    """
    트레이너의 운동기록관리 페이지를 반환합니다.
    """
    return templates.TemplateResponse("trainer/exercise_management.html", {
        "request": request,
        "user_name": current_user.get("name", "Unknown"),
        "user_type": current_user.get("user_type", "Unknown")
    })

@router.get("/exercise-records/{member_id}", response_class=HTMLResponse)
async def exercise_records_page(
    request: Request, 
    member_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """
    특정 회원의 운동 기록 페이지를 반환합니다.
    """
    # 회원이 현재 트레이너의 회원인지 확인
    member = db.query(Member)\
        .join(UserMember, UserMember.member_id == Member.id)\
        .filter(
            Member.id == member_id,
            UserMember.trainer_id == current_user["sub"]
        ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")

    return templates.TemplateResponse("trainer/exercise_records.html", {
        "request": request,
        "user_name": current_user.get("name", "Unknown"),
        "user_type": current_user.get("user_type", "Unknown"),
        "member": member
    })

@router.get("/exercise-recommendation", response_class=HTMLResponse)
async def exercise_recommendation_page(request: Request, current_user: dict = Depends(verify_trainer)):
    """
    트레이너의 추천운동관리 페이지를 반환합니다.
    """
    return templates.TemplateResponse("trainer/exercise_recommendation.html", {
        "request": request,
        "user_name": current_user.get("name", "Unknown"),
        "user_type": current_user.get("user_type", "Unknown")
    }) 