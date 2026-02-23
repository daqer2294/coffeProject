from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int):
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int):
        user = User(telegram_id=telegram_id)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create(self, telegram_id: int):
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            return user
        return await self.create(telegram_id)
