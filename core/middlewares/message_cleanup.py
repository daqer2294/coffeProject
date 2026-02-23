from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


class MessageCleanupMiddleware(BaseMiddleware):

    async def __call__(self, handler, event, data):

        state: FSMContext = data.get("state")
        bot = data.get("bot")

        # Получаем старые ID
        old_message_id = None
        old_chat_id = None

        if state:
            stored = await state.get_data()
            old_message_id = stored.get("bot_message_id")
            old_chat_id = stored.get("bot_chat_id")

        # Выполняем хендлер
        result = await handler(event, data)

        # Нас интересуют только Message
        if isinstance(result, Message) and state:

            # Удаляем старое сообщение
            if old_message_id and old_chat_id:
                try:
                    await bot.delete_message(
                        chat_id=old_chat_id,
                        message_id=old_message_id
                    )
                except:
                    pass

            # Сохраняем новое
            await state.update_data(
                bot_message_id=result.message_id,
                bot_chat_id=result.chat.id
            )

        return result
