from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService
from app.core.security import get_current_user
from app.models.base import get_db
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/api/v1/users",
    tags=["사용자"]
)

@router.post("/signup", response_model=UserResponse)
async def create_user(
    email: str = Form(...),
    name: str = Form(...),
    birth_date: str = Form(...),
    password: str = Form(...),
    user_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """회원가입"""
    try:
        user_data = UserCreate(
            email=email,
            name=name,
            birth_date=birth_date,
            password=password,
            user_type=user_type
        )
        new_user = await UserService.create_user(user_data, db)
        return jsonable_encoder(new_user)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회"""
    return current_user 