from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import verify_trainer
from app.models.pt_session import PTSession
from app.models.member_model import Member
from app.models.users_members import UserMember
from datetime import datetime, date
from typing import List
import logging

router = APIRouter(
    prefix="/api/v1/pt-sessions",
    tags=["PT Sessions"]
)

@router.get("/members")
async def get_pt_members(
    response: Response,
    skip: int = Query(default=0, description="Skip first N items"),
    limit: int = Query(default=10, description="Limit the number of items"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """
    현재 트레이너의 모든 회원 목록을 조회합니다.
    """
    try:
        # 트레이너의 모든 회원 조회 (PT 횟수와 관계없이)
        members = db.query(Member)\
            .join(UserMember, UserMember.member_id == Member.id)\
            .filter(UserMember.trainer_id == current_user["sub"])\
            .order_by(Member.sequence_number)\
            .offset(skip)\
            .limit(limit)\
            .all()

        # 각 회원의 현재 수업 회차와 다음 수업 일정 조회
        for member in members:
            # 현재 수업 회차 계산 (완료된 수업 수 + 1)
            completed_sessions = db.query(func.count(PTSession.id))\
                .filter(
                    PTSession.member_id == member.id,
                    PTSession.trainer_id == current_user["sub"],
                    PTSession.is_completed == True
                ).scalar()
            
            member.current_session_number = completed_sessions + 1

            # 다음 수업 일정 조회
            next_session = db.query(PTSession)\
                .filter(
                    PTSession.member_id == member.id,
                    PTSession.trainer_id == current_user["sub"],
                    PTSession.session_date >= date.today(),
                    PTSession.is_completed == False
                )\
                .order_by(PTSession.session_date, PTSession.start_time)\
                .first()

            if next_session:
                member.next_session_date = next_session.session_date.strftime("%Y-%m-%d")
            else:
                member.next_session_date = None

            # PT 관련 정보 추가
            member.total_pt_count = member.total_pt_count or 0
            member.remaining_pt_count = member.remaining_pt_count or 0

        # 전체 회원 수 조회 (PT 횟수와 관계없이)
        total_count = db.query(Member)\
            .join(UserMember, UserMember.member_id == Member.id)\
            .filter(UserMember.trainer_id == current_user["sub"])\
            .count()

        response.headers["X-Total-Count"] = str(total_count)
        
        return members

    except Exception as e:
        logging.error(f"PT 회원 목록 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{member_id}/schedule")
async def schedule_pt_session(
    member_id: str,
    session_date: date,
    start_time: str,
    end_time: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """
    회원의 PT 수업을 예약합니다.
    """
    try:
        # 회원 조회 및 권한 확인
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

        if member.remaining_pt_count <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="남은 PT 횟수가 없습니다."
            )

        # 현재 회차 계산
        current_session = db.query(func.count(PTSession.id))\
            .filter(
                PTSession.member_id == member_id,
                PTSession.trainer_id == current_user["sub"]
            ).scalar() + 1

        # 새로운 PT 세션 생성
        new_session = PTSession(
            member_id=member_id,
            trainer_id=current_user["sub"],
            session_number=current_session,
            session_date=session_date,
            start_time=datetime.strptime(start_time, "%H:%M").time(),
            end_time=datetime.strptime(end_time, "%H:%M").time()
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return new_session

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"PT 수업 예약 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 