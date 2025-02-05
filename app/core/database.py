import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import logging

# .env 파일 로드
load_dotenv()

# 환경변수 확인을 위한 디버그 출력
print("Database connection info:")
print(f"USER: {os.getenv('MYSQL_USER')}")
print(f"HOST: {os.getenv('MYSQL_HOST')}")
print(f"DATABASE: {os.getenv('MYSQL_DATABASE')}")

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

if not all([MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE]):
    raise ValueError("Missing database configuration. Please check your .env file.")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"

# SQLAlchemy 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 세션 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()

# DB 세션 핸들러
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logging.error(f"❌ 데이터베이스 세션 오류 발생: {e}")
        raise
    finally:
        db.close() 