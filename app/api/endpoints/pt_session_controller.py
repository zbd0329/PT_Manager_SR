from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import verify_trainer
from app.models.pt_session import PTSession
from app.models.member_model import Member
from app.models.users_members import UserMember
from app.models.exercise_record import ExerciseRecord
from datetime import datetime, date
from typing import List
import logging
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(
    prefix="/api/v1/pt-sessions",
    tags=["PT Sessions"]
)

class ExerciseCreate(BaseModel):
    exercise_name: str
    duration: int  # 초 단위
    repetitions: int
    body_part: str

class SessionCreate(BaseModel):
    session_date: str
    start_time: str
    end_time: str
    exercises: List[ExerciseCreate]

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
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """
    새로운 PT 세션과 운동 기록을 등록합니다.
    """
    try:
        # 회원 확인
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
            session_date=datetime.strptime(session_data.session_date, "%Y-%m-%d").date(),
            start_time=datetime.strptime(session_data.start_time, "%H:%M").time(),
            end_time=datetime.strptime(session_data.end_time, "%H:%M").time()
        )
        db.add(new_session)
        db.flush()  # ID 생성을 위해 flush

        # 운동 기록 생성
        for exercise in session_data.exercises:
            exercise_record = ExerciseRecord(
                session_id=new_session.id,
                exercise_name=exercise.exercise_name,
                duration=exercise.duration,
                repetitions=exercise.repetitions,
                body_part=exercise.body_part,
                input_source="TRAINER",
                member_id=member_id,
                trainer_id=current_user["sub"]
            )
            db.add(exercise_record)

        # 잔여 PT 횟수 차감
        member.remaining_pt_count = member.remaining_pt_count - 1
        
        db.commit()
        return {"message": "PT 세션과 운동 기록이 성공적으로 등록되었습니다."}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"PT 세션 등록 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{member_id}")
async def get_member_sessions(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """
    특정 회원의 PT 세션 목록을 조회합니다.
    """
    try:
        # 회원이 현재 트레이너의 회원인지 확인
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

        # PT 세션 목록 조회
        sessions = db.query(PTSession)\
            .filter(
                PTSession.member_id == member_id,
                PTSession.trainer_id == current_user["sub"]
            )\
            .order_by(PTSession.session_date, PTSession.start_time)\
            .all()

        # 응답 데이터 구성
        response_data = {
            "member_info": {
                "id": member.id,
                "name": member.name,
                "total_pt_count": member.total_pt_count,
                "remaining_pt_count": member.remaining_pt_count
            },
            "sessions": [{
                "id": session.id,
                "session_number": session.session_number,
                "session_date": session.session_date.strftime("%Y-%m-%d"),
                "start_time": session.start_time.strftime("%H:%M"),
                "end_time": session.end_time.strftime("%H:%M"),
                "is_completed": session.is_completed
            } for session in sessions]
        }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"PT 세션 목록 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{session_id}/exercises")
async def get_session_exercises(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """
    특정 PT 세션의 운동 기록을 조회합니다.
    """
    try:
        # PT 세션 조회
        session = db.query(PTSession)\
            .filter(
                PTSession.id == session_id,
                PTSession.trainer_id == current_user["sub"]
            ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PT 세션을 찾을 수 없습니다."
            )

        # 운동 기록 조회
        exercises = db.query(ExerciseRecord)\
            .filter(ExerciseRecord.session_id == session_id)\
            .all()

        # 응답 데이터 구성
        response_data = {
            "session_info": {
                "id": session.id,
                "session_number": session.session_number,
                "session_date": session.session_date.strftime("%Y-%m-%d"),
                "start_time": session.start_time.strftime("%H:%M"),
                "end_time": session.end_time.strftime("%H:%M"),
                "is_completed": session.is_completed
            },
            "exercises": [{
                "id": exercise.id,
                "exercise_name": exercise.exercise_name,
                "duration": exercise.duration,
                "repetitions": exercise.repetitions,
                "body_part": exercise.body_part
            } for exercise in exercises]
        }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"운동 기록 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{session_id}")
async def update_session(
    session_id: str,
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """
    PT 세션과 운동 기록을 수정합니다.
    """
    try:
        # PT 세션 조회
        session = db.query(PTSession)\
            .filter(
                PTSession.id == session_id,
                PTSession.trainer_id == current_user["sub"]
            ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PT 세션을 찾을 수 없습니다."
            )

        # 세션 정보 업데이트
        session.session_date = datetime.strptime(session_data.session_date, "%Y-%m-%d").date()
        session.start_time = datetime.strptime(session_data.start_time, "%H:%M").time()
        session.end_time = datetime.strptime(session_data.end_time, "%H:%M").time()

        # 기존 운동 기록 삭제
        db.query(ExerciseRecord)\
            .filter(ExerciseRecord.session_id == session_id)\
            .delete()

        # 새로운 운동 기록 생성
        for exercise in session_data.exercises:
            exercise_record = ExerciseRecord(
                session_id=session_id,
                exercise_name=exercise.exercise_name,
                duration=exercise.duration,
                repetitions=exercise.repetitions,
                body_part=exercise.body_part,
                input_source="TRAINER",
                member_id=session.member_id,
                trainer_id=current_user["sub"]
            )
            db.add(exercise_record)

        db.commit()
        return {"message": "PT 세션과 운동 기록이 성공적으로 수정되었습니다."}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"PT 세션 수정 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """
    PT 세션과 관련된 운동 기록을 모두 삭제합니다.
    """
    try:
        # PT 세션 조회
        session = db.query(PTSession)\
            .filter(
                PTSession.id == session_id,
                PTSession.trainer_id == current_user["sub"]
            ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PT 세션을 찾을 수 없습니다."
            )

        # 회원의 잔여 PT 횟수 증가 (세션 삭제로 인한 복구)
        member = db.query(Member).filter(Member.id == session.member_id).first()
        if member:
            member.remaining_pt_count = member.remaining_pt_count + 1

        # PT 세션 삭제 (cascade로 인해 관련 운동 기록도 자동 삭제됨)
        db.delete(session)
        db.commit()

        return {"message": "PT 세션과 운동 기록이 성공적으로 삭제되었습니다."}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"PT 세션 삭제 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 