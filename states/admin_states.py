from aiogram.fsm.state import StatesGroup, State


class AdminMessageStates(StatesGroup):
    waiting_for_telegram_id = State()
    waiting_for_text = State()
    confirming = State()