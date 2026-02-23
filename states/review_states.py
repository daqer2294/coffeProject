from aiogram.fsm.state import StatesGroup, State


class ReviewStates(StatesGroup):
    choosing_shop = State()
    choosing_date = State()
    rating_taste = State()
    rating_staff = State()
    rating_cleanliness = State()
    rating_speed = State()
    rating_price_value = State()
    comment = State()
    improvement = State()
