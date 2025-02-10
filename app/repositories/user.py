from sqlalchemy.orm import Session
from app.models.user import User, pwd_context
from app.schemas.user import UserCreate

class UserRepository:
    @staticmethod
    async def create_user(user: UserCreate, db: Session) -> User:
        hashed_password = pwd_context.hash(user.password)
        db_user = User(
            email=user.email,
            name=user.name,
            birth_date=user.birth_date,
            user_type=user.user_type,
            password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    async def get_user_by_email(email: str, db: Session) -> User:
        return db.query(User).filter(User.email == email).first() 