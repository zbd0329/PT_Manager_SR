from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer
from app.core.config import settings

security = HTTPBearer()

def create_access_token(data: dict) -> str:
    """JWT 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    print(f"Creating token with data: {to_encode}")  # 디버그 로그 추가
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """JWT 토큰 검증"""
    try:
        print(f"Raw token: {token}")
        # Bearer 접두사 제거
        if token.startswith('Bearer '):
            token = token.split(' ')[1]
            
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        print(f"Decoded token payload: {payload}")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError as e:
        print(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_from_cookie(request: Request) -> dict:
    """쿠키에서 토큰을 읽어 사용자 정보를 반환"""
    token = request.cookies.get("access_token")
    print("\n=== Cookie Token Debug ===")
    print(f"Raw cookie token: {token}")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Bearer 접두사 제거
        if token.startswith('Bearer '):
            token = token.split(' ')[1]
            print(f"Token after Bearer removal: {token}")
        
        payload = verify_token(token)
        print(f"Decoded payload: {payload}")
        print("=== End Cookie Token Debug ===\n")
        return payload
        
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 검증 실패",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_trainer(current_user: dict = Depends(get_current_user_from_cookie)) -> dict:
    """트레이너 권한 확인"""
    print("\n=== Trainer Verification Debug ===")
    raw_user_type = current_user.get("user_type", "")
    user_type = raw_user_type.strip().upper()
    
    print(f"Full current_user data: {current_user}")
    print(f"Raw user_type: {raw_user_type!r}")
    print(f"Processed user_type: {user_type!r}")
    print(f"Comparison result: {user_type == 'TRAINER'}")
    print("=== End Trainer Verification Debug ===\n")
    
    if user_type != "TRAINER":
        print(f"Access denied. Expected: 'TRAINER', Got: {user_type!r}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="트레이너만 접근할 수 있는 페이지입니다."
        )
    return current_user

def verify_member(current_user: dict = Depends(get_current_user_from_cookie)) -> dict:
    """회원 권한 확인"""
    raw_user_type = current_user.get("user_type", "")
    user_type = raw_user_type.strip().upper()
    
    print(f"Verifying member access:")
    print(f"  - Raw user_type: {raw_user_type!r}")
    print(f"  - Processed user_type: {user_type!r}")
    print(f"  - Expected: 'MEMBER'")
    print(f"  - Comparison result: {user_type == 'MEMBER'}")
    
    if user_type != "MEMBER":
        print(f"Access denied. Expected: 'MEMBER', Got: {user_type!r}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="회원만 접근할 수 있는 페이지입니다."
        )
    return current_user 