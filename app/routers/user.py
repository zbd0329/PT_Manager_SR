from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserType, pwd_context
from ..schemas.user import UserCreate, UserResponse, UserLogin
from datetime import timedelta
from ..auth.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/signup", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to create user with ID: {user.id}")
        
        # 기존 사용자 확인
        db_user = db.query(User).filter(User.id == user.id).first()
        if db_user:
            raise HTTPException(status_code=400, detail="이미 등록된 ID입니다")
        
        # user_type 검증 (Enum의 value와 비교)
        if user.user_type not in UserType:  # Enum 멤버십 검사
            raise HTTPException(status_code=400, detail="잘못된 사용자 유형입니다")
        
        # 비밀번호 암호화
        hashed_password = pwd_context.hash(user.password)
        
        # 새 사용자 생성
        new_user = User(
            id=user.id,
            name=user.name,
            birth_date=user.birth_date,
            password_hash=hashed_password,
            user_type=user.user_type  # Enum 객체 그대로 사용
        )
        
        # DB 쿼리 실행 전
        logger.info("About to execute database query")
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info("User created successfully")
        return new_user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        logger.exception("Full error traceback:")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        logger.info(f"Login attempt for user: {user_data.id}, type: {user_data.user_type}")
        
        # 사용자 찾기
        db_user = db.query(User).filter(User.id == user_data.id).first()
        if not db_user:
            logger.warning(f"User not found: {user_data.id}")
            raise HTTPException(status_code=401, detail="아이디가 존재하지 않습니다")
        
        # 사용자 유형 확인
        if db_user.user_type != user_data.user_type:
            logger.warning(f"User type mismatch. DB: {db_user.user_type}, Input: {user_data.user_type}")
            raise HTTPException(status_code=401, detail="사용자 유형이 일치하지 않습니다")
        
        # 비밀번호 확인
        if not pwd_context.verify(user_data.password, db_user.password_hash):
            logger.warning(f"Invalid password for user: {user_data.id}")
            raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다")
        
        # JWT 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": db_user.id,
                "user_type": db_user.user_type.value,
                "name": db_user.name
            },
            expires_delta=access_token_expires
        )
        
        logger.info(f"Login successful for user: {user_data.id}")
        return {
            "message": "로그인 성공",
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": db_user.user_type.value,
            "user_name": db_user.name
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=f"로그인 처리 중 오류가 발생했습니다: {str(e)}") 