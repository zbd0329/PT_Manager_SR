from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    # 프로젝트 기본 설정
    PROJECT_NAME: str = "PT Manager"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 데이터베이스 설정
    MYSQL_HOST: str = "db-324ec9-kr.vpc-pub-cdb.ntruss.com"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "sara"
    MYSQL_PASSWORD: str = "saraonly1!"
    MYSQL_DATABASE: str = "money-distributor"
    DATABASE_URL: str = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

    # JWT 설정
    JWT_SECRET_KEY: str = "52933503178b82f4beb1bd2f022c19d018e9d875110e8f43ccb1f11c4ab90699"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'
        extra = "allow"  # 추가 환경 변수 허용

# settings 인스턴스 생성
settings = Settings()

# settings를 명시적으로 export
__all__ = ["settings"] 