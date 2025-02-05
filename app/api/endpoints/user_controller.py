from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin
from app.services.user_service import UserService
from app.core.database import get_db
from app.core.security import create_access_token
from typing import List
import logging

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
        400: 이미 존재하는 아이디 또는 이메일
    """
    try:
        # 아이디 중복 체크
        existing_user = await UserService.get_user_by_login_id(user.login_id, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login ID already registered"
            )
        
        # 이메일이 제공된 경우 중복 체크
        if user.email:
            existing_email = await UserService.get_user_by_email(user.email, db)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        print(f"Creating user with data: {user.dict()}")  # 디버그 로그
        return await UserService.create_user(user, db)
    except Exception as e:
        print(f"Error creating user: {str(e)}")  # 디버그 로그
        raise

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
    print(f"Login attempt - Login ID: {user_data.login_id}, Type: {user_data.user_type}")  # 디버그 로그
    
    user = await UserService.authenticate_user(user_data.login_id, user_data.password, user_data.user_type, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login ID, password or user type"
        )
    
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "user_type": user.user_type.value,
            "login_id": user.login_id
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.name,
        "user_type": user.user_type.value
    }