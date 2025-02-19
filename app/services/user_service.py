from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.models.user_model import User, UserType

class UserService:
    @staticmethod
    async def create_user(user: UserCreate, db: Session) -> User:
        """
        새로운 사용자를 생성합니다.
        
        Args:
            user: 생성할 사용자 정보
            db: 데이터베이스 세션
            
        Returns:
            생성된 사용자 객체
        """
        return await UserRepository.create_user(user, db)

    @staticmethod
    async def get_user_by_email(email: str, db: Session) -> User:
        """
        이메일로 사용자를 조회합니다.
        
        Args:
            email: 조회할 사용자의 이메일
            db: 데이터베이스 세션
            
        Returns:
            조회된 사용자 객체 또는 None
        """
        return await UserRepository.get_user_by_email(email, db)

    @staticmethod
    async def authenticate_user(email: str, password: str, user_type: str, db: Session) -> User:
        """
        사용자 인증을 수행합니다.
        
        Args:
            email: 사용자 이메일
            password: 비밀번호
            user_type: 사용자 유형 (문자열: 'member' 또는 'trainer')
            db: 데이터베이스 세션
            
        Returns:
            인증된 사용자 객체 또는 None
        """
        print(f"Authenticating - Email: {email}, Type: {user_type}")  # 디버그 로그
        user = await UserRepository.get_user_by_email(email, db)
        
        if not user:
            print("User not found")  # 디버그 로그
            return None
            
        if not user.verify_password(password):
            print("Invalid password")  # 디버그 로그
            return None
            
        # 문자열 값 비교
        if user.user_type.value != user_type:
            print(f"User type mismatch - Expected: {user_type}, Found: {user.user_type.value}")  # 디버그 로그
            return None
            
        return user 