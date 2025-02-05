from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin
from app.services.user_service import UserService
from app.core.database import get_db
from app.core.security import create_access_token
from typing import List
import logging
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserType

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
async def trainer_login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    트레이너 로그인을 처리합니다.
    
    Args:
        user_data: 로그인 정보
        response: FastAPI Response 객체
        db: 데이터베이스 세션
        
    Returns:
        access_token과 사용자 정보
        
    Raises:
        401: 잘못된 인증 정보
        403: 권한 없음
    """
    print("\n=== 트레이너 로그인 디버그 ===")
    print(f"수신된 데이터: {user_data}")
    print(f"login_id: {user_data.login_id}")
    print(f"user_type: {user_data.user_type}")
    print("=== 디버그 끝 ===\n")
    
    try:
        # Users 테이블에서 트레이너 조회
        user = await UserRepository.get_user_by_login_id(user_data.login_id, db)
        
        if not user or not user.verify_password(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="아이디 또는 비밀번호가 올바르지 않습니다."
            )
            
        # 트레이너 권한 확인
        if user.user_type != UserType.TRAINER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="트레이너 계정이 아닙니다."
            )
        
        print(f"트레이너 로그인 성공 - ID: {user.login_id}")
        
        # login_id 정제
        clean_login_id = ''.join(char for char in str(user.login_id) if char.isprintable())
        print("\n=== Login Token Creation Debug ===")
        print(f"Original login_id: {user.login_id!r}")
        print(f"Cleaned login_id: {clean_login_id!r}")
        
        # 토큰 데이터 준비
        token_data = {
            "sub": str(user.id),
            "user_type": "TRAINER",
            "login_id": clean_login_id
        }
        print(f"Token data before creation: {token_data}")
        
        access_token = create_access_token(data=token_data)
        print(f"Generated access token: {access_token[:20]}...")
        
        # HTTP-only 쿠키에 토큰 설정
        cookie_value = f"Bearer {access_token}"
        print(f"Cookie value to be set: {cookie_value[:30]}...")
        
        response.set_cookie(
            key="access_token",
            value=cookie_value,
            httponly=True,
            secure=False,  # 개발 환경에서는 False, 프로덕션에서는 True로 설정
            samesite="lax",
            max_age=1800  # 30분
        )
        
        response_data = {
            "token_type": "bearer",
            "user_name": user.name,
            "user_type": "TRAINER"
        }
        print(f"Response data: {response_data}")
        print("=== End Login Token Creation Debug ===\n")
        
        # Content-Type 헤더 추가
        response.headers["Content-Type"] = "application/json"
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"트레이너 로그인 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다."
        )