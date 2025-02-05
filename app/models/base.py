from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 데이터베이스 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # SQL 실행 로그 출력 (디버깅용)
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()

# 데이터베이스 세션 생성 함수 (Dependency Injection 용)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
