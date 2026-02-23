import os
from openpyxl import Workbook
from datetime import datetime

from database.session import async_session
from repositories.review_repo import ReviewRepository


class ExportService:

    EXPORT_DIR = "exports"

    async def export_reviews_to_excel(self) -> str:
        # 1️⃣ Создаём папку если её нет
        os.makedirs(self.EXPORT_DIR, exist_ok=True)

        wb = Workbook()
        ws = wb.active
        ws.title = "Отзывы"

        # 2️⃣ Заголовки
        headers = [
            "ID",
            "Пользователь",
            "Кофейня",
            "Дата визита",
            "Вкус",
            "Персонал",
            "Чистота",
            "Скорость",
            "Цена/качество",
            "Комментарий",
            "Улучшение",
        ]

        ws.append(headers)

        # 3️⃣ Получаем данные
        async with async_session() as session:
            repo = ReviewRepository(session)
            visits = await repo.get_all_visits_with_details()

        # 4️⃣ Заполняем строки
        for visit in visits:
            ratings = {r.criterion_key: r.rating for r in visit.ratings}

            ws.append([
                visit.id,
                visit.user.telegram_id if visit.user else "",
                visit.shop.name if visit.shop else "",
                str(visit.visit_date),
                ratings.get("taste"),
                ratings.get("staff"),
                ratings.get("cleanliness"),
                ratings.get("speed"),
                ratings.get("price_value"),
                visit.text.comment if visit.text else "",
                visit.text.improvement_suggestion if visit.text else "",
            ])

        # 5️⃣ Формируем путь
        filename = f"reviews_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.EXPORT_DIR, filename)

        # 6️⃣ Сохраняем файл
        wb.save(filepath)

        return filepath
