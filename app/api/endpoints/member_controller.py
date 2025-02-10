from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.member_schema import MemberCreate, MemberResponse, MemberUpdate, MemberLogin
from app.models.member_model import Member
from app.models.pt_session import PTSession
from app.core.security import get_current_user_from_cookie, create_access_token, verify_trainer
from passlib.context import CryptContext
from app.models.user_model import UserType
from app.models.users_members import UserMember
import logging
from typing import List
from sqlalchemy.sql import func
from app.models.exercise_record import ExerciseRecord

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
    current_user: dict = Depends(verify_trainer)
):
    """트레이너의 회원 목록을 조회합니다."""
    try:
        # 현재 트레이너와 연결된 회원들만 조회 (sequence_number로 정렬)
        members = db.query(
            Member.id,
            Member.sequence_number,
            Member.name,
            Member.login_id,
            Member.gender,
            Member.contact,
            Member.fitness_goal,
            Member.experience_level,
            Member.session_duration,
            Member.total_pt_count,
            Member.remaining_pt_count,
            Member.has_injury,
            Member.created_at,
            Member.is_active
        ).join(UserMember, UserMember.member_id == Member.id)\
            .filter(UserMember.trainer_id == current_user["sub"])\
            .order_by(Member.sequence_number)\
            .offset(skip)\
            .limit(limit)\
            .all()

        # 전체 회원 수 조회
        total_count = db.query(Member)\
            .join(UserMember, UserMember.member_id == Member.id)\
            .filter(UserMember.trainer_id == current_user["sub"])\
            .count()

        # 응답 헤더에 전체 개수 추가
        response.headers["X-Total-Count"] = str(total_count)
        
        return members
    except Exception as e:
        logging.error(f"회원 목록 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/", response_model=MemberResponse)
async def create_member(
    member: MemberCreate,
    current_user: dict = Depends(verify_trainer),
    db: Session = Depends(get_db)
):
    """새로운 회원을 생성하고 현재 트레이너와 연결합니다."""
    try:
        # 요청 데이터 로깅
        print("\n=== Member Creation Debug ===")
        print(f"Received member data: {member.dict()}")
        print(f"Current user: {current_user}")
        
        # 데이터 유효성 검사 로깅
        print("\nValidating member data:")
        print(f"login_id: {member.login_id} (min_length=4)")
        print(f"password: {'*' * len(member.password)} (min_length=6)")
        print(f"name: {member.name} (min_length=2)")
        print(f"gender: {member.gender}")
        print(f"contact: {member.contact}")
        print(f"fitness_goal: {member.fitness_goal}")
        print(f"experience_level: {member.experience_level}")
        print(f"has_injury: {member.has_injury}")
        print(f"injury_description: {member.injury_description}")
        print(f"session_duration: {member.session_duration}")
        print(f"preferred_exercises: {member.preferred_exercises}")
        print(f"total_pt_count: {member.total_pt_count}")
        print(f"remaining_pt_count: {member.remaining_pt_count}")
        print(f"notes: {member.notes}")
        
        # 회원 ID 중복 체크
        existing_member = db.query(Member).filter(Member.login_id == member.login_id).first()
        if existing_member:
            print(f"Duplicate login_id found: {member.login_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 회원 ID입니다."
            )

        # 현재 트레이너의 마지막 회원 순번 조회
        last_sequence = db.query(func.max(Member.sequence_number))\
            .join(UserMember, UserMember.member_id == Member.id)\
            .filter(UserMember.trainer_id == current_user["sub"])\
            .scalar()
        
        # 첫 번째 회원이면 1, 아니면 마지막 순번 + 1
        next_sequence = 1 if last_sequence is None else last_sequence + 1
        print(f"Next sequence number: {next_sequence}")

        # 새 회원 생성
        new_member = Member(
            login_id=member.login_id,
            name=member.name,
            gender=member.gender,
            contact=member.contact,
            fitness_goal=member.fitness_goal,
            experience_level=member.experience_level,
            has_injury=member.has_injury,
            injury_description=member.injury_description,
            session_duration=member.session_duration,
            preferred_exercises=member.preferred_exercises,
            total_pt_count=member.total_pt_count,
            remaining_pt_count=member.remaining_pt_count,
            notes=member.notes,
            sequence_number=next_sequence
        )
        new_member.set_password(member.password)
        print(f"Created new member object: {new_member.__dict__}")
        
        db.add(new_member)
        db.flush()  # ID 생성을 위해 flush

        # 트레이너-회원 관계 생성
        user_member = UserMember(
            trainer_id=current_user["sub"],
            member_id=new_member.id
        )
        db.add(user_member)
        
        db.commit()
        db.refresh(new_member)
        print("Successfully created member and relationship")
        print("=== End Member Creation Debug ===\n")
        
        return new_member
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error during member creation: {str(e)}")
        logging.error(f"회원 생성 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{member_id}")
async def get_member_info(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """회원 정보를 조회합니다."""
    try:
        # 현재 트레이너의 회원인지 확인
        member = db.query(Member)\
            .join(UserMember, UserMember.member_id == Member.id)\
            .filter(
                Member.id == member_id,
                UserMember.trainer_id == current_user["sub"]
            ).first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="회원을 찾을 수 없습니다."
            )
        
        # 회원의 운동 기록 조회
        exercise_records = db.query(
            ExerciseRecord.exercise_name,
            ExerciseRecord.duration,
            ExerciseRecord.repetitions,
            ExerciseRecord.sets,
            ExerciseRecord.body_part
        ).join(
            PTSession, PTSession.id == ExerciseRecord.session_id
        ).filter(
            ExerciseRecord.member_id == member_id
        ).order_by(
            PTSession.session_date.desc(),
            ExerciseRecord.created_at.desc()
        ).limit(10).all()  # 최근 10개의 운동 기록만 가져옴
        
        # 운동 기록을 딕셔너리 리스트로 변환
        exercise_history = [
            {
                "exercise_name": record.exercise_name,
                "duration": record.duration,
                "repetitions": record.repetitions,
                "sets": record.sets,
                "body_part": record.body_part
            }
            for record in exercise_records
        ]
        
        return {
            "id": member.id,
            "name": member.name,
            "gender": member.gender.value,
            "contact": member.contact,
            "fitness_goal": member.fitness_goal,
            "experience_level": member.experience_level.value,
            "has_injury": member.has_injury,
            "injury_description": member.injury_description,
            "session_duration": member.session_duration,
            "preferred_exercises": member.preferred_exercises,
            "total_pt_count": member.total_pt_count,
            "remaining_pt_count": member.remaining_pt_count,
            "notes": member.notes,
            "exercise_history": exercise_history  # 운동 기록 추가
        }
            
    except Exception as e:
        logging.error(f"회원 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: str,
    member_update: MemberUpdate,
    current_user: dict = Depends(verify_trainer),
    db: Session = Depends(get_db)
):
    """회원 정보를 수정합니다."""
    try:
        # 현재 트레이너의 회원인지 확인
        member = db.query(Member)\
            .join(UserMember, UserMember.member_id == Member.id)\
            .filter(
                Member.id == member_id,
                UserMember.trainer_id == current_user["sub"]
            ).first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="회원을 찾을 수 없습니다."
            )

        # 업데이트할 필드 설정
        update_data = member_update.dict(exclude_unset=True)
        
        # 비밀번호가 제공된 경우 해시화
        if "password" in update_data:
            member.set_password(update_data.pop("password"))

        # 나머지 필드 업데이트
        for field, value in update_data.items():
            setattr(member, field, value)

        db.commit()
        db.refresh(member)
        
        return member
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"회원 정보 수정 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login")
async def member_login(member_data: MemberLogin, response: Response, db: Session = Depends(get_db)):
    """회원 로그인을 처리합니다."""
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