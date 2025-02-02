from fastapi import FastAPI
from .database import engine, Base
# from mangum import Mangum #Vercel 배포 하기위한 임포트

app = FastAPI(title="PTTracker")

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to PTTracker"}

# DB 연결 테스트 엔드포인트
@app.get("/db-test")
def test_db_connection():
    """데이터베이스 연결을 확인하는 엔드포인트"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT DATABASE();")
            return {"message": "DB 연결 성공!", "database": result.fetchone()}
    except Exception as e:
        return {"error": str(e)}

# Vercel용 핸들러 추가
# handler = Mangum(app) 