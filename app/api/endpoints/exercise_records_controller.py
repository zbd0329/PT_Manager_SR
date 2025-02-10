from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_trainer
from app.models.exercise_record import ExerciseRecord
from app.models.pt_session import PTSession
from typing import List
import logging

router = APIRouter(prefix="/api/v1/exercise-records", tags=["exercise-records"])

@router.get("/session/{session_id}")
async def get_session_exercise_records(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """특정 PT 세션의 운동 기록을 조회합니다."""
    try:
        # PT 세션 존재 여부 확인
        session = db.query(PTSession).filter(PTSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PT 세션을 찾을 수 없습니다."
            )

        # 운동 기록 조회
        exercise_records = db.query(
            ExerciseRecord.exercise_name,
            ExerciseRecord.duration,
            ExerciseRecord.repetitions,
            ExerciseRecord.sets,
            ExerciseRecord.body_part
        ).filter(
            ExerciseRecord.session_id == session_id
        ).order_by(
            ExerciseRecord.created_at
        ).all()

        # 운동 기록을 딕셔너리 리스트로 변환
        exercises = [
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
            "session_id": session_id,
            "session_number": session.session_number,
            "exercises": exercises
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"운동 기록 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 