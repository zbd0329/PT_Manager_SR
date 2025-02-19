from sqlalchemy.orm import Session
from app.models.user_model import User, pwd_context
from app.schemas.user_schema import UserCreate
import uuid

class UserRepository:
    @staticmethod
    async def create_user(user: UserCreate, db: Session) -> User:
        db_user = User(
            email=user.email,
            name=user.name,
            birth_date=user.birth_date,
            user_type=user.user_type
        )
        db_user.set_password(user.password)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    async def get_user_by_email(email: str, db: Session) -> User:
        return db.query(User).filter(User.email == email).first() 