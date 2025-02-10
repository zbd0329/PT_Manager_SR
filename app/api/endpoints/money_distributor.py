from fastapi import APIRouter, Query, Header
from typing import Optional
from app.schemas.response import ResponseModel
from app.services.money_distributor import MoneyDistributorService

router = APIRouter(
    prefix="/api/v1/money",
    tags=["돈 뿌리기"]
)

@router.post("/spread", response_model=ResponseModel)
async def create_spread(
    amount: int = Query(..., description="뿌릴 금액", gt=0),
    count: int = Query(..., description="뿌릴 인원 수", gt=0),
    user_id: int = Header(..., alias="X-USER-ID"),
    room_id: str = Header(..., alias="X-ROOM-ID")
):
    """돈 뿌리기를 생성합니다."""
    result = await MoneyDistributorService.process_distribution(amount, count, user_id, room_id)
    return ResponseModel(
        success=True,
        message="돈 뿌리기가 생성되었습니다.",
        data=result
    ) 