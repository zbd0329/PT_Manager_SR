from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.core.security import create_access_token
from app.models.base import get_db
from sqlalchemy.orm import Session

class UserService:
    @staticmethod
    async def create_user(user: UserCreate, db: Session) -> UserResponse:
        """사용자 생성"""
        existing_user = await UserRepository.get_user_by_email(user.email, db)
        if existing_user:
            raise ValueError("이미 존재하는 이메일입니다.")
        
        new_user = await UserRepository.create_user(user, db)
        return UserResponse.from_orm(new_user)

    @staticmethod
    def authenticate_user(email: str, password: str):
        """사용자 인증"""
        db = next(get_db())
        user = UserRepository.get_user_by_email(email, db)
        if not user or not user.verify_password(password):
            return None
        return user 