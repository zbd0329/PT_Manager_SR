from pydantic import BaseModel, constr
from datetime import date
from ..models.user import UserType

class UserCreate(BaseModel):
    id: str
    name: str
    birth_date: date
    password: constr(min_length=8)  # 최소 8자 이상
    user_type: UserType

class UserLogin(BaseModel):
    id: str
    password: str
    user_type: UserType

class UserResponse(BaseModel):
    id: str
    name: str
    birth_date: date
    user_type: UserType

    class Config:
        orm_mode = True 