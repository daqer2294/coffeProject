from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from keyboards.main_menu import main_menu_keyboard
from keyboards.reply_global import global_reply_keyboard

router = Router()


# =====================================================
# 🚀 /start
# =====================================================
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    return await message.answer(
        "☕ Добро пожаловать!\n\nВыберите действие:",
        reply_markup=main_menu_keyboard(message.from_user.id)
    )


# =====================================================
# 🏠 Кнопка «Главное меню»
# =====================================================
@router.message(F.text == "🏠 Главное меню")
async def handle_main_menu(message: Message, state: FSMContext):
    await state.clear()

    return await message.answer(
        "☕ Добро пожаловать!\n\nВыберите действие:",
        reply_markup=main_menu_keyboard(message.from_user.id)
    )
