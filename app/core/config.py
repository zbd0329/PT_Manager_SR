from functools import lru_cache
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Get the absolute path to the .env file
env_path = Path('.env').resolve()
print(f"\n=== Environment Loading Debug ===")
print(f"Looking for .env at: {env_path}")
print(f"Does .env file exist? {env_path.exists()}")

# Load environment variables only once
load_dotenv(dotenv_path=env_path, override=True)

# Debug: Print environment variables (safely)
api_key = os.getenv('OPENAI_API_KEY', '')
print("\nEnvironment variables check:")
print(f"OPENAI_API_KEY exists: {bool(api_key)}")
print(f"OPENAI_API_KEY length: {len(api_key)}")
print(f"OPENAI_API_KEY preview: {api_key[:10]}...")
print(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL')}")
print(f"Current working directory: {os.getcwd()}")

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "PT Manager"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "money-distributor")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # OpenAI settings
    OPENAI_API_KEY: str = api_key  # Use the already loaded API key
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

    class Config:
        env_file = env_path
        case_sensitive = True
        env_file_encoding = 'utf-8'

    def model_post_init(self, *args, **kwargs):
        print("\nSettings initialization check:")
        print(f"OpenAI API Key exists: {bool(self.OPENAI_API_KEY)}")
        if self.OPENAI_API_KEY:
            print(f"OpenAI API Key length: {len(self.OPENAI_API_KEY)}")
            print(f"OpenAI API Key preview: {self.OPENAI_API_KEY[:10]}...")
        print(f"OpenAI Model: {self.OPENAI_MODEL}")
        db_url = self.DATABASE_URL.replace(self.MYSQL_PASSWORD, "****") if self.DATABASE_URL else "Not set"
        print(f"Database URL: {db_url}")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# Final verification
print("\nFinal Settings verification:")
print(f"Settings OPENAI_API_KEY exists: {bool(settings.OPENAI_API_KEY)}")
print(f"Settings OPENAI_API_KEY length: {len(settings.OPENAI_API_KEY)}")
print(f"Settings OPENAI_API_KEY preview: {settings.OPENAI_API_KEY[:10]}...")
print(f"Settings OPENAI_MODEL: {settings.OPENAI_MODEL}")