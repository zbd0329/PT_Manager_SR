from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import UserService
from app.core.security import verify_token_middleware
from app.models.user_model import UserType
from typing import List
from app.schemas.user_schema import UserResponse

router = APIRouter(
    prefix="/api/v1/member-management",
    tags=["Member Management"]
)

@router.get("/members", response_model=List[UserResponse])
async def get_all_members(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token_middleware)
):
    """
    모든 회원 목록을 조회합니다. (트레이너만 접근 가능)
    """
    # 토큰에서 사용자 유형 확인
    if token_data.get("user_type") != "trainer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers can access this endpoint"
        )
    
    # 회원 목록 조회 (user_type이 'member'인 사용자만)
    members = await UserService.get_all_members(db)
    return members

@router.get("/members/{member_id}", response_model=UserResponse)
async def get_member_detail(
    member_id: str,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token_middleware)
):
    """
    특정 회원의 상세 정보를 조회합니다. (트레이너만 접근 가능)
    """
    if token_data.get("user_type") != "trainer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers can access this endpoint"
        )
    
    member = await UserService.get_user_by_id(member_id, db)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    if member.user_type != UserType.MEMBER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified user is not a member"
        )
    
    return member 