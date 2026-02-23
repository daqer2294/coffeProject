from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import settings


def main_menu_keyboard(user_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(text="📝 Оставить отзыв", callback_data="create_review")
    builder.button(text="📋 Мои отзывы", callback_data="my_reviews")

    # Кнопки только для админа
    if user_id in settings.ADMIN_IDS:
        builder.button(text="📊 Скачать Excel", callback_data="admin_export")
        builder.button(text="✉ Написать пользователю", callback_data="admin_write_user")

    builder.adjust(1)

    return builder.as_markup()