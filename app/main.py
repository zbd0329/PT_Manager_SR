from fastapi import FastAPI
from .database import engine, Base
from mangum import Mangum

app = FastAPI(title="PTTracker")

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to PTTracker"}

# Vercel용 핸들러 추가
handler = Mangum(app) 