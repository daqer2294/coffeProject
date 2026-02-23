from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_shops_keyboard(shops):
    buttons = []

    for shop in shops:
        buttons.append([
            InlineKeyboardButton(
                text=shop.name,
                callback_data=f"shop_{shop.id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
