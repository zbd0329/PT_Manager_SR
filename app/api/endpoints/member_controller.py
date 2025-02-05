from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.member_schema import MemberCreate, MemberResponse, MemberUpdate, MemberLogin
from app.models.member_model import Member
from app.core.security import get_current_user_from_cookie, create_access_token
from passlib.context import CryptContext
from app.models.user_model import UserType
import logging
from typing import List

router = APIRouter(
    prefix="/api/v1/members",
    tags=["Members"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/", response_model=List[MemberResponse])
async def get_members(
    response: Response,
    skip: int = Query(default=0, description="Skip first N items"),
    limit: int = Query(default=10, description="Limit the number of items"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    트레이너의 회원 목록을 조회합니다.
    """
    if current_user.get("user_type") != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="트레이너만 회원 목록을 조회할 수 있습니다."
        )

    # 전체 회원 수 조회
    total_count = db.query(Member)\
        .filter(Member.trainer_id == current_user.get("sub"))\
        .count()

    # 페이지네이션된 회원 목록 조회
    members = db.query(Member)\
        .filter(Member.trainer_id == current_user.get("sub"))\
        .offset(skip)\
        .limit(limit)\
        .all()

    # Response 헤더에 전체 개수 추가
    response.headers["X-Total-Count"] = str(total_count)
    return members

@router.post("/", response_model=MemberResponse)
async def create_member(
    member: MemberCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    새로운 회원을 등록합니다.
    """
    # 트레이너 권한 확인
    if current_user.get("user_type") != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="트레이너만 회원을 등록할 수 있습니다."
        )

    # 로그인 ID 중복 확인
    if db.query(Member).filter(Member.login_id == member.login_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 로그인 ID입니다."
        )

    # 새 회원 생성
    db_member = Member(
        login_id=member.login_id,
        name=member.name,
        gender=member.gender,
        contact=member.contact,
        pt_count=member.pt_count,
        notes=member.notes,
        trainer_id=current_user.get("sub"),  # JWT 토큰에서 트레이너 ID 추출
        password=pwd_context.hash(member.password)
    )

    try:
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원 등록 중 오류가 발생했습니다."
        )

@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    특정 회원의 정보를 조회합니다.
    """
    if current_user.get("user_type") != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="트레이너만 회원 정보를 조회할 수 있습니다."
        )

    member = db.query(Member)\
        .filter(Member.id == member_id)\
        .filter(Member.trainer_id == current_user.get("sub"))\
        .first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다."
        )

    return member

@router.put("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: str,
    member_update: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    회원 정보를 수정합니다.
    """
    if current_user.get("user_type") != "TRAINER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="트레이너만 회원 정보를 수정할 수 있습니다."
        )

    db_member = db.query(Member)\
        .filter(Member.id == member_id)\
        .filter(Member.trainer_id == current_user.get("sub"))\
        .first()

    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다."
        )

    # 업데이트할 필드 설정
    for field, value in member_update.dict(exclude_unset=True).items():
        if field == "password" and value:
            value = pwd_context.hash(value)
        setattr(db_member, field, value)

    try:
        db.commit()
        db.refresh(db_member)
        return db_member
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원 정보 수정 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/login")
async def member_login(member_data: MemberLogin, response: Response, db: Session = Depends(get_db)):
    """
    회원 로그인을 처리합니다.
    
    Args:
        member_data: 로그인 정보
        response: FastAPI Response 객체
        db: 데이터베이스 세션
        
    Returns:
        access_token과 회원 정보
        
    Raises:
        401: 잘못된 인증 정보
        403: 비활성화된 회원
    """
    print(f"회원 로그인 시도 - ID: {member_data.login_id}")
    
    try:
        # Members 테이블에서 회원 조회
        member = db.query(Member).filter(Member.login_id == member_data.login_id).first()
        
        if not member or not pwd_context.verify(member_data.password, member.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="아이디 또는 비밀번호가 올바르지 않습니다."
            )
            
        # 회원 활성화 상태 확인
        if not member.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="비활성화된 회원 아이디입니다. 트레이너에게 문의해주세요."
            )
        
        print(f"회원 로그인 성공 - ID: {member.login_id}")
        
        # login_id 정제
        clean_login_id = ''.join(char for char in str(member.login_id) if char.isprintable())
        print(f"Original login_id: {member.login_id!r}")
        print(f"Cleaned login_id: {clean_login_id!r}")
        
        # 토큰 데이터 준비
        token_data = {
            "sub": str(member.id),
            "user_type": "MEMBER",
            "login_id": clean_login_id
        }
        print(f"Token data before creation: {token_data}")
        
        access_token = create_access_token(data=token_data)
        
        # HTTP-only 쿠키에 토큰 설정
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,  # 개발 환경에서는 False, 프로덕션에서는 True로 설정
            samesite="lax",
            max_age=1800  # 30분
        )
        
        response_data = {
            "token_type": "bearer",
            "user_name": member.name,
            "user_type": "MEMBER"
        }
        print(f"Response data: {response_data}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"회원 로그인 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다."
        )