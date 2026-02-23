from datetime import date
from typing import Dict, Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Visit, ReviewRating, ReviewText


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ==================================================
    # Проверка — существует ли уже отзыв
    # ==================================================
    async def exists_for_date(
        self,
        user_id: int,
        shop_id: int,
        visit_date: date
    ) -> Optional[Visit]:

        stmt = select(Visit).where(
            Visit.user_id == user_id,
            Visit.shop_id == shop_id,
            Visit.visit_date == visit_date,
            Visit.status == "completed"
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # ==================================================
    # Создание визита
    # ==================================================
    async def create_visit(
        self,
        user_id: int,
        shop_id: int,
        visit_date: date
    ) -> Visit:

        visit = Visit(
            user_id=user_id,
            shop_id=shop_id,
            visit_date=visit_date,
            status="completed"
        )

        self.session.add(visit)
        await self.session.commit()
        await self.session.refresh(visit)

        return visit

    # ==================================================
    # Добавление оценок
    # ==================================================
    async def add_ratings(
        self,
        visit_id: int,
        ratings: Dict[str, int]
    ) -> None:

        objects = [
            ReviewRating(
                visit_id=visit_id,
                criterion_key=key,
                rating=value
            )
            for key, value in ratings.items()
        ]

        self.session.add_all(objects)
        await self.session.commit()

    # ==================================================
    # Добавление текста
    # ==================================================
    async def add_text(
        self,
        visit_id: int,
        comment: Optional[str],
        improvement: Optional[str]
    ) -> None:

        text = ReviewText(
            visit_id=visit_id,
            comment=comment,
            improvement_suggestion=improvement
        )

        self.session.add(text)
        await self.session.commit()

    # ==================================================
    # Получить ВСЕ активные визиты пользователя
    # ==================================================
    async def get_user_visits(self, user_id: int) -> List[Visit]:

        stmt = (
            select(Visit)
            .where(
                Visit.user_id == user_id,
                Visit.status == "completed"
            )
            .options(
                selectinload(Visit.shop),
                selectinload(Visit.ratings),
                selectinload(Visit.text)
            )
            .order_by(Visit.created_at.desc())
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    # ==================================================
    # Получить конкретный визит
    # ==================================================
    async def get_visit_with_details(
        self,
        visit_id: int
    ) -> Optional[Visit]:

        stmt = (
            select(Visit)
            .where(
                Visit.id == visit_id,
                Visit.status == "completed"
            )
            .options(
                selectinload(Visit.shop),
                selectinload(Visit.ratings),
                selectinload(Visit.text)
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # ==================================================
    # Soft delete
    # ==================================================
    async def mark_deleted(self, visit_id: int) -> bool:

        stmt = select(Visit).where(Visit.id == visit_id)
        result = await self.session.execute(stmt)
        visit = result.scalar_one_or_none()

        if not visit:
            return False

        visit.status = "deleted"
        await self.session.commit()
        return True

    # ==================================================
    # Для админа — ВСЕ визиты (включая deleted)
    # ==================================================
    async def get_all_visits_with_details(self) -> List[Visit]:

        stmt = (
            select(Visit)
            .options(
                selectinload(Visit.user),
                selectinload(Visit.shop),
                selectinload(Visit.ratings),
                selectinload(Visit.text)
            )
            .order_by(Visit.id.desc())
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()
