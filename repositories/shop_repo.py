from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import CoffeeShop


class ShopRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self):
        result = await self.session.execute(
            select(CoffeeShop).where(CoffeeShop.is_active == True)
        )
        return result.scalars().all()

    async def get_by_id(self, shop_id: int):
        result = await self.session.execute(
            select(CoffeeShop).where(CoffeeShop.id == shop_id)
        )
        return result.scalar_one_or_none()

    async def create(self, name: str, address: str):
        shop = CoffeeShop(
            name=name,
            address=address,
            is_active=True
        )
        self.session.add(shop)
        await self.session.commit()
        await self.session.refresh(shop)
        return shop
