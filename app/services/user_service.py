from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.models.user_model import User, UserType
from app.models.member_model import Member
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    async def authenticate_user(login_id: str, password: str, user_type: str, db: Session) -> User:
        """
        사용자 인증을 수행합니다.
        
        Args:
            login_id: 로그인 ID
            password: 비밀번호
            user_type: 사용자 유형 (trainer 또는 member)
            db: 데이터베이스 세션
            
        Returns:
            인증된 사용자 객체 또는 None
            
        Raises:
            ValueError: 비활성화된 회원 계정인 경우
        """
        print(f"=== 인증 시작 ===")
        print(f"로그인 시도 - ID: {login_id}, 유형: {user_type}")

        if user_type == UserType.TRAINER.value:
            print("트레이너 인증 프로세스 시작")
            # 트레이너는 Users 테이블에서 조회
            user = await UserRepository.get_user_by_login_id(login_id, db)
            
            if not user:
                print(f"트레이너 계정을 찾을 수 없음: {login_id}")
                return None
                
            print(f"트레이너 계정 조회 성공 - 유형: {user.user_type.value}")
                
            if not user.verify_password(password):
                print("트레이너 비밀번호 불일치")
                return None
                
            if user.user_type != UserType.TRAINER:
                print(f"사용자 유형 불일치 - 예상: {UserType.TRAINER}, 실제: {user.user_type}")
                return None
                
            print("트레이너 인증 성공")
            return user
            
        elif user_type == UserType.MEMBER.value:
            print("회원 인증 프로세스 시작")
            # 회원은 Members 테이블에서 조회
            member = db.query(Member).filter(Member.login_id == login_id).first()
            
            if not member:
                print(f"회원 계정을 찾을 수 없음: {login_id}")
                return None
                
            print("회원 계정 조회 성공")
                
            if not pwd_context.verify(password, member.password):
                print("회원 비밀번호 불일치")
                return None
                
            # 회원 활성화 상태 체크
            if not member.is_active:
                print(f"비활성화된 회원 계정: {login_id}")
                raise ValueError("비활성화된 회원 아이디입니다. 트레이너에게 문의해주세요.")
                
            print("회원 인증 성공 - User 객체로 변환")
            # Member 객체를 User 객체로 변환
            user = User(
                id=member.id,
                login_id=member.login_id,
                name=member.name,
                user_type=UserType.MEMBER,
                password=member.password  # 이미 해시된 비밀번호
            )
            print("인증 완료 - 변환된 User 객체 반환")
            return user
            
        print(f"지원하지 않는 사용자 유형: {user_type}")
        return None

    @staticmethod
    async def get_user_by_login_id(login_id: str, db: Session) -> User:
        """
        로그인 ID로 사용자를 조회합니다.
        
        Args:
            login_id: 조회할 사용자의 로그인 ID
            db: 데이터베이스 세션
            
        Returns:
            조회된 사용자 객체 또는 None
        """
        return await UserRepository.get_user_by_login_id(login_id, db)