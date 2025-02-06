from app.models import Base as AppBase  # 모든 모델이 정의된 파일
import sys
import os

from fastapi import FastAPI, Request, HTTPException, Depends
from app.core.database import engine, Base
# from mangum import Mangum #Vercel 배포 하기위한 임포트
from sqlalchemy import text
from app.api.endpoints import user_router
from app.api.endpoints.member_controller import router as member_router
from app.api.endpoints.trainer_controller import router as trainer_router
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.security import verify_token, verify_trainer, verify_member
from fastapi import status

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# 데이터베이스 테이블 생성
print("Creating database tables...")  # 디버그 로그
AppBase.metadata.create_all(bind=engine)
print("Database initialization completed!")  # 디버그 로그

# 라우터 등록
app.include_router(user_router)
app.include_router(member_router)
app.include_router(trainer_router)

# 정적 파일 설정 (상대 경로 사용)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

security = HTTPBearer()

async def verify_token_middleware(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token or expired token"
        )
    return payload

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# DB 연결 테스트 엔드포인트
@app.get("/db-test")
def test_db_connection():
    """데이터베이스 연결을 확인하는 엔드포인트"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE()"))
            return {"message": "DB 연결 성공!", "database": result.scalar()}
    except Exception as e:
        return {"error": str(e)}

# Vercel용 핸들러 추가
# handler = Mangum(app)

# 회원가입 페이지 라우트 추가
@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/member/dashboard")
async def member_dashboard(request: Request, current_user: dict = Depends(verify_member)):
    return templates.TemplateResponse("member/dashboard.html", {"request": request})

@app.get("/trainer/dashboard")
async def trainer_dashboard(request: Request, current_user: dict = Depends(verify_trainer)):
    """트레이너 대시보드 페이지"""
    print("\n=== Trainer Dashboard Access Debug ===")
    print(f"Request cookies: {request.cookies}")
    print(f"Current user data: {current_user}")
    print("=== End Dashboard Debug ===\n")
    return templates.TemplateResponse("trainer/dashboard.html", {
        "request": request,
        "user_name": current_user.get("name", "Unknown"),
        "user_type": current_user.get("user_type", "Unknown")
    })

@app.get("/trainer/member-management")
async def member_management(request: Request, current_user: dict = Depends(verify_trainer)):
    """회원 관리 페이지를 반환합니다."""
    return templates.TemplateResponse("trainer/member_management.html", {"request": request})

@app.get("/api/member/verify-auth")
async def verify_auth(request: Request):
    """토큰 유효성을 검증하는 엔드포인트"""
    try:
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 토큰이 없습니다."
            )
            
        # Bearer 접두사 제거
        if token.startswith('Bearer '):
            token = token.split(' ')[1]
            
        payload = verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다."
            )
            
        return {"status": "authenticated", "user_data": payload}
        
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증에 실패했습니다."
        )