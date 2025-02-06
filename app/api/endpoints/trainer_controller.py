from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.security import verify_trainer

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