from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
import calendar

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_calendar_keyboard(page: str = "current") -> InlineKeyboardMarkup:
    """
    page = "current" или "previous"
    """

    tz = ZoneInfo("Asia/Irkutsk")
    today = datetime.now(tz).date()
    min_date = today - timedelta(days=30)

    builder = InlineKeyboardBuilder()

    # Определяем какой месяц показывать
    if page == "current":
        year = today.year
        month = today.month
    else:
        if today.month == 1:
            year = today.year - 1
            month = 12
        else:
            year = today.year
            month = today.month - 1

    month_name = date(year, month, 1).strftime("%B %Y")

    # Заголовок
    builder.row(
        InlineKeyboardButton(
            text=f"📅 {month_name.capitalize()}",
            callback_data="ignore"
        )
    )

    _, days_in_month = calendar.monthrange(year, month)

    buttons = []

    for day in range(1, days_in_month + 1):
        d = date(year, month, day)

        # Ограничение 30 дней
        if min_date <= d <= today:
            buttons.append(
                InlineKeyboardButton(
                    text=str(day),
                    callback_data=f"calendar_{d.isoformat()}"
                )
            )

    # Сетка 7 в ряд
    builder.row(*buttons, width=7)

    # Навигация
    if page == "current":
        builder.row(
            InlineKeyboardButton(
                text="◀ Предыдущий месяц",
                callback_data="calendar_nav_previous"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="▶ Текущий месяц",
                callback_data="calendar_nav_current"
            )
        )

    return builder.as_markup()
