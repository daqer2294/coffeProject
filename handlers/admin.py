from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import settings
from services.export_service import ExportService
from states.admin_states import AdminMessageStates

from database.session import async_session
from repositories.user_repo import UserRepository
from repositories.admin_message_repo import AdminMessageRepository

from core.bot import bot


router = Router()


# =========================================================
# 📊 EXPORT EXCEL
# =========================================================

@router.callback_query(F.data == "admin_export")
async def handle_admin_export(callback: CallbackQuery):
    await callback.answer()

    if callback.from_user.id not in settings.ADMIN_IDS:
        return

    service = ExportService()
    filename = await service.export_reviews_to_excel()

    file = FSInputFile(filename)

    await callback.message.answer_document(file)


# =========================================================
# ✉ START WRITING
# =========================================================

@router.callback_query(F.data == "admin_write_user")
async def start_write_user(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.from_user.id not in settings.ADMIN_IDS:
        return

    await state.set_state(AdminMessageStates.waiting_for_telegram_id)

    await callback.message.answer(
        "Введите telegram_id пользователя (как в Excel):"
    )


# =========================================================
# 👤 TELEGRAM ID
# =========================================================

@router.message(AdminMessageStates.waiting_for_telegram_id)
async def process_telegram_id(message: Message, state: FSMContext):

    if not message.text.isdigit():
        return await message.answer("ID должен быть числом.")

    telegram_id = int(message.text)

    async with async_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        return await message.answer("Пользователь с таким telegram_id не найден.")

    await state.update_data(
        telegram_id=telegram_id,
        user_db_id=user.id
    )

    await state.set_state(AdminMessageStates.waiting_for_text)

    await message.answer("Введите сообщение для отправки:")


# =========================================================
# 📝 MESSAGE TEXT
# =========================================================

@router.message(AdminMessageStates.waiting_for_text)
async def process_message_text(message: Message, state: FSMContext):

    await state.update_data(text=message.text)

    data = await state.get_data()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_admin_send"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_admin_send"),
            ]
        ]
    )

    await state.set_state(AdminMessageStates.confirming)

    await message.answer(
        f"📨 Вы отправляете сообщение пользователю:\n\n"
        f"Telegram ID: {data['telegram_id']}\n\n"
        f"Текст:\n{data['text']}",
        reply_markup=keyboard
    )


# =========================================================
# ❌ CANCEL
# =========================================================

@router.callback_query(F.data == "cancel_admin_send")
async def cancel_admin_send(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer("Отправка отменена.")


# =========================================================
# ✅ CONFIRM SEND
# =========================================================

@router.callback_query(F.data == "confirm_admin_send")
async def confirm_admin_send(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.from_user.id not in settings.ADMIN_IDS:
        return

    data = await state.get_data()

    telegram_id = data["telegram_id"]
    user_db_id = data["user_db_id"]
    text = data["text"]

    status = "sent"

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=f"📢 Сообщение от администрации:\n\n{text}"
        )
    except Exception:
        status = "failed"

    async with async_session() as session:
        repo = AdminMessageRepository(session)

        await repo.create(
            admin_telegram_id=callback.from_user.id,
            user_id=user_db_id,
            text=text,
            status=status,
        )

    await state.clear()

    if status == "sent":
        await callback.message.answer("✅ Сообщение успешно отправлено.")
    else:
        await callback.message.answer(
            "⚠ Не удалось отправить сообщение (пользователь мог заблокировать бота)."
        )