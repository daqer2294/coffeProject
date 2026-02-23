from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def global_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )
