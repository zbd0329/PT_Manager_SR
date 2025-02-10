from app.repositories.money_distributor import MoneyDistributorRepository
from app.utils.token_generator import generate_unique_token

class MoneyDistributorService:
    @staticmethod
    async def process_distribution(amount: int, count: int, user_id: int, room_id: str):
        token = generate_unique_token()
        return await MoneyDistributorRepository.save_distribution(
            token=token,
            amount=amount,
            count=count,
            user_id=user_id,
            room_id=room_id
        ) 