from typing import Dict, Optional
from datetime import timedelta, date
from utils.datetime_utils import get_today
from repositories.review_repo import ReviewRepository


class ReviewService:

    # Можно оставить отзыв за последние 30 дней
    MAX_DAYS_BACK = 30

    def __init__(self, review_repo: ReviewRepository):
        self.review_repo = review_repo

    # --------------------------------------------------
    # Проверка допустимости даты
    # --------------------------------------------------
    def validate_visit_date(self, visit_date: date) -> None:
        today = get_today()

        # Будущая дата
        if visit_date > today:
            raise ValueError("Нельзя оставить отзыв за будущую дату.")

        # Слишком старая дата
        if visit_date < today - timedelta(days=self.MAX_DAYS_BACK):
            raise ValueError(
                "Отзыв можно оставить только за последние 30 дней."
            )

    # --------------------------------------------------
    # Создание полного отзыва
    # --------------------------------------------------
    async def create_full_review(
        self,
        user_id: int,
        shop_id: int,
        visit_date: date,
        ratings: Dict[str, int],
        comment: Optional[str],
        improvement: Optional[str]
    ):

        # 1️⃣ Проверяем дату
        self.validate_visit_date(visit_date)

        # 2️⃣ Проверяем, нет ли уже отзыва
        existing = await self.review_repo.exists_for_date(
            user_id=user_id,
            shop_id=shop_id,
            visit_date=visit_date
        )

        if existing:
            raise ValueError(
                "Вы уже оставляли отзыв за эту дату."
            )

        # 3️⃣ Создаём визит
        visit = await self.review_repo.create_visit(
            user_id=user_id,
            shop_id=shop_id,
            visit_date=visit_date
        )

        # 4️⃣ Добавляем оценки
        await self.review_repo.add_ratings(
            visit_id=visit.id,
            ratings=ratings
        )

        # 5️⃣ Добавляем текст
        await self.review_repo.add_text(
            visit_id=visit.id,
            comment=comment,
            improvement=improvement
        )

        # 6️⃣ Считаем среднюю оценку
        avg = sum(ratings.values()) / len(ratings)

        return {
            "visit_id": visit.id,
            "average_rating": round(avg, 2)
        }
