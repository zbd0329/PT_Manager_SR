from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from pathlib import Path
from functools import lru_cache
from typing import Optional

# 프로젝트 루트 디렉토리 찾기
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# .env 파일 로드
print("\n=== 환경 변수 로드 디버그 ===")
env_path = os.path.join(BASE_DIR, '.env')
print(f"env 파일 경로: {env_path}")
print(f"env 파일 존재 여부: {os.path.exists(env_path)}")

# .env 파일 내용 확인
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        print("\n.env 파일 내용:")
        for line in f:
            if line.strip() and not line.startswith('#'):
                key = line.split('=')[0]
                print(f"{key}: {'*' * 10 if 'KEY' in key or 'PASSWORD' in key else '설정됨'}")

# 환경 변수 로드
load_dotenv(env_path)

# 환경 변수 확인
print("\n환경 변수 확인:")
print(f"OPENAI_API_KEY 존재 여부: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL')}")
print(f"MYSQL_HOST: {os.getenv('MYSQL_HOST')}")
print(f"현재 작업 디렉토리: {os.getcwd()}")
print("=== 환경 변수 로드 디버그 끝 ===\n")

class Settings(BaseSettings):
    # 프로젝트 기본 설정
    PROJECT_NAME: str = "PT Manager"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 데이터베이스 설정
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "money-distributor")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # JWT 설정
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # OpenAI 설정
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'
        extra = "allow"  # 추가 환경 변수 허용

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("\n=== Settings 초기화 디버그 ===")
        print(f"OPENAI_API_KEY 존재 여부: {bool(self.OPENAI_API_KEY)}")
        if self.OPENAI_API_KEY:
            print(f"OPENAI_API_KEY 길이: {len(self.OPENAI_API_KEY)}")
            print(f"OPENAI_API_KEY 앞부분: {self.OPENAI_API_KEY[:10]}...")
        print(f"OPENAI_MODEL: {self.OPENAI_MODEL}")
        db_url = self.DATABASE_URL.replace(self.MYSQL_PASSWORD, "****") if self.DATABASE_URL else "Not set"
        print(f"DATABASE_URL: {db_url}")
        print("=== Settings 초기화 디버그 끝 ===\n")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# settings 인스턴스 생성
settings = get_settings()

# settings를 명시적으로 export
__all__ = ["settings"] 