from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_trainer
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from app.core.config import settings
from typing import List, Optional
from pydantic import BaseModel
import json
from app.models.recommended_workout import RecommendedWorkout, RecommendedExercise
from app.models.pt_session import PTSession
from app.models.body_measurement_model import BodyMeasurement
from datetime import datetime
import os

router = APIRouter(prefix="/api/v1/recommended-workouts", tags=["recommended-workouts"])

class Exercise(BaseModel):
    exercise_name: str
    sets: int
    repetitions: int
    duration: int
    rest_time: int
    description: str

class WorkoutPlan(BaseModel):
    total_duration: int
    exercises: List[Exercise]

class GenerateWorkoutRequest(BaseModel):
    member_id: str
    member_name: str
    gender: str
    fitness_goal: str
    pt_duration: int
    preferred_exercises: Optional[List[str]] = []
    remaining_sessions: int
    injuries: Optional[List[str]] = []
    session_id: str
    exercise_history: Optional[List[dict]] = []
    exercise_level: str

@router.post("/generate")
async def generate_workout(
    request: GenerateWorkoutRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """OpenAI API를 사용하여 회원에게 맞는 운동을 추천합니다."""
    try:
        print("\n=== LangChain OpenAI 요청 디버그 시작 ===")
        print("1. 요청 데이터 확인:")
        print(f"Request body: {request.dict()}")
        
        # 회원의 최신 신체 계측 정보 조회
        latest_measurement = db.query(BodyMeasurement)\
            .filter(BodyMeasurement.member_id == request.member_id)\
            .order_by(BodyMeasurement.measurement_date.desc())\
            .first()
            
        # 신체 계측 정보 문자열 생성
        body_measurement_str = ""
        if latest_measurement:
            body_measurement_str = f"""
- 신체 계측 정보 (최근 측정일: {latest_measurement.measurement_date}):
  * 키: {latest_measurement.height}cm
  * 몸무게: {latest_measurement.weight}kg
  * BMI: {latest_measurement.bmi}
  * 체지방량: {latest_measurement.body_fat}kg
  * 체지방률: {latest_measurement.body_fat_percentage}%
  * 골격근량: {latest_measurement.muscle_mass}kg"""
        
        print("\n2. OpenAI 설정 확인:")
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"API Key 존재 여부: {bool(api_key)}")
        print(f"API Key 길이: {len(api_key) if api_key else 0}")
        print(f"API Key 앞부분: {api_key[:10]}..." if api_key else "API 키 없음")
        print(f"Model: {settings.OPENAI_MODEL}")
        
        if not api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
        
        # LangChain ChatOpenAI 객체 생성
        llm = ChatOpenAI(
            temperature=settings.OPENAI_TEMPERATURE,
            model_name=settings.OPENAI_MODEL,
            openai_api_key=api_key,
            openai_api_base=os.getenv("OPENAI_API_BASE"),
            streaming=False
        )
        print("✅ ChatOpenAI 모델 초기화 성공")

        # 최근 운동 기록 문자열 생성
        exercise_history_str = ""
        if request.exercise_history:
            exercise_history_str = "\n최근 운동 기록:\n"
            for idx, exercise in enumerate(request.exercise_history, 1):
                exercise_history_str += f"{idx}. {exercise['exercise_name']} - {exercise['sets']}세트 {exercise['repetitions']}회 ({exercise['duration']}초), 부위: {exercise['body_part']}\n"

        # 프롬프트 구성
        prompt = f"""
당신은 전문 PT 트레이너입니다. 다음 회원 정보를 바탕으로 운동 프로그램을 추천해주세요.

회원 정보:
- 이름: {request.member_name}
- 성별: {request.gender}
- 운동 목표: {request.fitness_goal}
- PT 시간: {request.pt_duration}분
- 운동 수준: {request.exercise_level}
- 선호하는 운동: {', '.join(request.preferred_exercises) if request.preferred_exercises else '없음'}
- 남은 PT 횟수: {request.remaining_sessions}회
- 부상 이력: {', '.join(request.injuries) if request.injuries else '없음'}{body_measurement_str}
{exercise_history_str}

위 회원의 정보와 신체 계측 정보, 운동 기록을 참고하여, 적합한 운동 프로그램을 추천해주세요.
특히 BMI, 체지방률, 골격근량을 고려하여 운동 강도와 종류를 조절해주세요.
이전 운동 기록을 분석하여 운동 강도와 난이도를 조절하고, 부위별 균형을 고려해주세요.
pt시간에 맞춰서 운동계획을 짜주세요. 
준비운동과 마무리운동은 5분식 넣고 자세한 운동을 적어주세요. (준비운동과 마무리운동은 운동 시간에 포함되지 않습니다.)

응답은 반드시 다음 JSON 형식을 정확히 따라주세요:
{{
    "total_duration": <총 운동 시간(분)을 정수로 입력>,
    "exercises": [
        {{
            "exercise_name": <운동명을 문자열로 입력>,
            "sets": <세트 수를 정수로 입력>,
            "repetitions": <반복 횟수를 정수로 입력 (시간 유지가 필요한 경우에도 초 단위로 환산하여 repetitions에 입력)>,
            "duration": <1세트당 예상 소요 시간을 초 단위 정수로 입력>,
            "rest_time": <세트 간 휴식 시간을 초 단위 정수로 입력>,
            "description": <운동 방법 설명을 문자열로 입력>
        }}
    ]
}}

주의사항:
1. 모든 숫자는 반드시 정수로 입력해야 합니다.
2. 플랭크와 같이 시간 유지가 필요한 운동의 경우, repetitions에 초 단위로 환산하여 입력하세요.
3. JSON 형식을 정확히 지켜주세요.
"""
        print(f"\n3. 프롬프트 내용:")
        print(prompt)

        # 콜백으로 토큰 사용량 추적
        with get_openai_callback() as cb:
            # 질의 실행
            response = llm.invoke(prompt)
            print("\n4. API 응답 성공")
            
            # 토큰 사용량 출력
            print(f"\n5. 토큰 사용량:")
            print(f"프롬프트 토큰: {cb.prompt_tokens}")
            print(f"응답 토큰: {cb.completion_tokens}")
            print(f"총 토큰: {cb.total_tokens}")
            print(f"총 비용: ${cb.total_cost:.6f}")

            # JSON 파싱
            workout_json = json.loads(response.content)
            print(f"\n6. 파싱된 JSON:\n{workout_json}")
            
            # Pydantic 모델로 변환하여 검증
            workout_plan = WorkoutPlan(**workout_json)
            print(f"\n7. 최종 응답 데이터:\n{workout_plan.dict()}")
            
            print("=== LangChain OpenAI 요청 디버그 종료 ===\n")
            return workout_plan

    except Exception as e:
        print(f"\n=== 오류 발생 ===")
        print(f"오류 타입: {type(e).__name__}")
        print(f"오류 내용: {str(e)}")
        print(f"=== 오류 디버그 종료 ===\n")
        raise HTTPException(
            status_code=500, 
            detail=f"AI 추천운동 생성에 실패했습니다: {str(e)}"
        )

class SaveWorkoutRequest(BaseModel):
    member_id: str
    session_id: str
    workout_plan: WorkoutPlan

@router.post("")
async def save_workout(
    request: SaveWorkoutRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """생성된 운동 프로그램을 저장합니다."""
    try:
        print("\n=== 운동 프로그램 저장 디버그 ===")
        print(f"요청 데이터: {request.dict()}")
        
        # 새로운 추천 운동 프로그램 생성
        workout = RecommendedWorkout(
            member_id=request.member_id,
            session_id=request.session_id,
            workout_name=f"{request.workout_plan.total_duration}분 운동 프로그램",
            total_duration=request.workout_plan.total_duration
        )
        print(f"생성할 운동 프로그램: {workout.__dict__}")
        
        db.add(workout)
        db.flush()  # ID 생성을 위해 flush
        print(f"생성된 운동 프로그램 ID: {workout.id}")

        # 운동 목록 저장
        for idx, exercise in enumerate(request.workout_plan.exercises, 1):
            exercise_record = RecommendedExercise(
                workout_id=workout.id,
                exercise_name=exercise.exercise_name,
                sets=exercise.sets,
                repetitions=exercise.repetitions,
                duration=exercise.duration,
                rest_time=exercise.rest_time,
                description=exercise.description,
                sequence=idx
            )
            db.add(exercise_record)
            print(f"운동 {idx} 추가: {exercise_record.__dict__}")

        db.commit()
        print("=== 운동 프로그램 저장 완료 ===\n")
        return {"message": "운동 프로그램이 성공적으로 저장되었습니다."}
        
    except Exception as e:
        print(f"\n=== 저장 중 오류 발생 ===")
        print(f"오류 타입: {type(e).__name__}")
        print(f"오류 내용: {str(e)}")
        print("=== 오류 디버그 종료 ===\n")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"운동 프로그램 저장 중 오류 발생: {str(e)}")

@router.get("")
async def get_recommended_workouts(
    member_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """회원의 추천 운동 프로그램 목록을 조회합니다."""
    try:
        query = db.query(
            RecommendedWorkout.id,
            RecommendedWorkout.workout_name,
            RecommendedWorkout.total_duration,
            RecommendedWorkout.created_at,
            RecommendedWorkout.updated_at
        )

        # 특정 회원의 운동 프로그램만 조회
        if member_id:
            query = query.filter(RecommendedWorkout.member_id == member_id)

        # 최신순으로 정렬
        workouts = query.order_by(RecommendedWorkout.created_at.desc()).all()

        return [{
            "id": workout.id,
            "workout_name": workout.workout_name,
            "total_duration": workout.total_duration,
            "created_at": workout.created_at,
            "updated_at": workout.updated_at
        } for workout in workouts]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"추천 운동 프로그램 조회 중 오류 발생: {str(e)}"
        )

@router.get("/{workout_id}")
async def get_recommended_workout_detail(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """특정 추천 운동 프로그램의 상세 정보를 조회합니다."""
    try:
        # 운동 프로그램 조회
        workout = db.query(RecommendedWorkout).filter(RecommendedWorkout.id == workout_id).first()
        if not workout:
            raise HTTPException(status_code=404, detail="운동 프로그램을 찾을 수 없습니다.")

        # 운동 목록 조회
        exercises = db.query(RecommendedExercise)\
            .filter(RecommendedExercise.workout_id == workout_id)\
            .order_by(RecommendedExercise.sequence)\
            .all()

        return {
            "id": workout.id,
            "workout_name": workout.workout_name,
            "total_duration": workout.total_duration,
            "created_at": workout.created_at,
            "updated_at": workout.updated_at,
            "exercises": [{
                "exercise_name": exercise.exercise_name,
                "sets": exercise.sets,
                "repetitions": exercise.repetitions,
                "duration": exercise.duration,
                "rest_time": exercise.rest_time,
                "description": exercise.description,
                "sequence": exercise.sequence
            } for exercise in exercises]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"운동 프로그램 상세 조회 중 오류 발생: {str(e)}"
        )

@router.get("/sessions/{member_id}")
async def get_member_pt_sessions(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_trainer)
):
    """회원의 PT 세션 목록을 조회합니다."""
    try:
        print(f"\n=== PT 세션 조회 디버그 ===")
        print(f"회원 ID: {member_id}")
        print(f"트레이너 ID: {current_user['sub']}")
        
        # 모든 PT 세션 조회 (완료 여부와 관계없이)
        sessions = db.query(
            PTSession.id,
            PTSession.session_number,
            PTSession.session_date,
            PTSession.start_time,
            PTSession.end_time,
            PTSession.is_completed
        ).filter(
            PTSession.member_id == member_id,
            PTSession.trainer_id == current_user["sub"]
        ).order_by(
            PTSession.session_date.desc(),
            PTSession.start_time.desc()
        ).limit(10).all()

        print(f"조회된 세션 수: {len(sessions)}")
        
        result = [{
            "id": session.id,
            "session_number": session.session_number,
            "session_date": session.session_date.strftime("%Y-%m-%d"),
            "start_time": str(session.start_time),
            "end_time": str(session.end_time),
            "is_completed": session.is_completed
        } for session in sessions]
        
        print(f"응답 데이터: {result}")
        print("=== PT 세션 조회 디버그 종료 ===\n")
        
        return result

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"PT 세션 목록 조회 중 오류 발생: {str(e)}"
        ) 