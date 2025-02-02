from app.models import Base as AppBase  # 모든 모델이 정의된 파일
import sys
import os

from fastapi import FastAPI, Request, HTTPException, Depends
from .database import engine, Base
# from mangum import Mangum #Vercel 배포 하기위한 임포트
from sqlalchemy import text
from .routers import user
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth.jwt import verify_token

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="PTTracker")

# 데이터베이스 테이블 생성
AppBase.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(user.router)

# 정적 파일 설정
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
async def member_dashboard(request: Request):
    return templates.TemplateResponse("member/dashboard.html", {"request": request})

@app.get("/trainer/dashboard")
async def trainer_dashboard(request: Request):
    return templates.TemplateResponse("trainer/dashboard.html", {"request": request})

@app.get("/api/member/verify-auth")
async def verify_auth(token_data: dict = Depends(verify_token_middleware)):
    return {"status": "authenticated", "user_data": token_data} 