from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def skip_keyboard(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏭ Пропустить",
                    callback_data=f"skip_{action}"
                )
            ]
        ]
    )
