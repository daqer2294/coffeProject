from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_rating_keyboard(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1 ⭐", callback_data=f"{prefix}_1"),
                InlineKeyboardButton(text="2 ⭐", callback_data=f"{prefix}_2"),
                InlineKeyboardButton(text="3 ⭐", callback_data=f"{prefix}_3"),
                InlineKeyboardButton(text="4 ⭐", callback_data=f"{prefix}_4"),
                InlineKeyboardButton(text="5 ⭐", callback_data=f"{prefix}_5"),
            ]
        ]
    )
