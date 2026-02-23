from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

REVIEWS_PER_PAGE = 3


# =====================================================
# 📋 Список отзывов
# =====================================================
def reviews_list_keyboard(visits, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    total_pages = (len(visits) - 1) // REVIEWS_PER_PAGE + 1
    start = page * REVIEWS_PER_PAGE
    end = start + REVIEWS_PER_PAGE
    page_visits = visits[start:end]

    # 3 отзыва вертикально
    for visit in page_visits:
        builder.add(
            InlineKeyboardButton(
                text=visit.shop.name,
                callback_data=f"review_detail:{visit.id}"
            )
        )

    builder.adjust(1)

    # Навигация
    if total_pages > 1:
        left_cb = f"reviews_page:{page - 1}" if page > 0 else "noop"
        right_cb = f"reviews_page:{page + 1}" if page < total_pages - 1 else "noop"

        builder.row(
            InlineKeyboardButton(text="◀", callback_data=left_cb),
            InlineKeyboardButton(text=f"{page + 1} / {total_pages}", callback_data="noop"),
            InlineKeyboardButton(text="▶", callback_data=right_cb),
        )

    return builder.as_markup()


# =====================================================
# 📄 Детали одного отзыва
# =====================================================
def review_detail_keyboard(visit_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="🗑 Удалить",
            callback_data=f"delete_review:{visit_id}"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text="⬅ Назад",
            callback_data="my_reviews"
        )
    )

    return builder.as_markup()


# =====================================================
# ⚠️ Подтверждение удаления
# =====================================================
def confirm_delete_keyboard(visit_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="✅ Подтвердить",
            callback_data=f"confirm_delete:{visit_id}"
        ),
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data=f"review_detail:{visit_id}"
        )
    )

    return builder.as_markup()
