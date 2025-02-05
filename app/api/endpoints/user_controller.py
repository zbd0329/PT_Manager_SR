from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin
from app.services.user_service import UserService
from app.core.database import get_db
from app.core.security import create_access_token
from typing import List

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    새로운 사용자를 생성합니다.
    
    Args:
        user: 생성할 사용자 정보
        db: 데이터베이스 세션
        
    Returns:
        생성된 사용자 정보
        
    Raises:
        400: 이미 존재하는 이메일
    """
    db_user = await UserService.get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return await UserService.create_user(user, db)

@router.post("/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    사용자 로그인을 처리합니다.
    
    Args:
        user_data: 로그인 정보
        db: 데이터베이스 세션
        
    Returns:
        access_token과 사용자 정보
        
    Raises:
        401: 잘못된 인증 정보
    """
    print(f"Login attempt - Email: {user_data.email}, Type: {user_data.user_type}")  # 디버그 로그
    
    # 데이터베이스에서 사용자 조회
    db_user = await UserService.get_user_by_email(user_data.email, db)
    if db_user:
        print(f"Found user - Email: {db_user.email}, Type: {db_user.user_type}")  # 디버그 로그
    
    user = await UserService.authenticate_user(user_data.email, user_data.password, user_data.user_type, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email, password or user type"
        )
    
    # Enum 값을 문자열로 변환
    access_token = create_access_token(data={"sub": user.email, "user_type": user.user_type.value})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.name,
        "user_type": user.user_type.value
    } 