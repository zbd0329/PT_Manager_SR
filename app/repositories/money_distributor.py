from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

class MoneyDistributorRepository:
    @staticmethod
    async def save_distribution(
        token: str,
        amount: int,
        count: int,
        user_id: int,
        room_id: str,
        db: AsyncSession = get_db()
    ):
        # DB 쿼리 로직
        query = """INSERT INTO distributions (token, amount, count, user_id, room_id)
                  VALUES (:token, :amount, :count, :user_id, :room_id)"""
        await db.execute(query, {
            "token": token,
            "amount": amount,
            "count": count,
            "user_id": user_id,
            "room_id": room_id
        })
        await db.commit()
        return {"token": token} 