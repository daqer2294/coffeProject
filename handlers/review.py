from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from states.review_states import ReviewStates
from keyboards.inline_shops import get_shops_keyboard
from keyboards.inline_ratings import get_rating_keyboard
from keyboards.inline_skip import skip_keyboard
from keyboards.inline_calendar import get_calendar_keyboard

from database.session import async_session
from repositories.shop_repo import ShopRepository
from repositories.review_repo import ReviewRepository
from repositories.user_repo import UserRepository
from services.review_service import ReviewService

from utils.texts import (
    choose_shop,
    rate_taste,
    rate_staff,
    rate_cleanliness,
    rate_speed,
    rate_price_value,
    ask_comment,
    ask_improvement,
)

router = Router()


# =========================================================
# 🚀 START REVIEW
# =========================================================

@router.callback_query(F.data == "create_review")
async def start_review(callback: CallbackQuery, state: FSMContext) -> Message:
    await callback.answer()

    async with async_session() as session:
        repo = ShopRepository(session)
        shops = await repo.get_all()

    await state.set_state(ReviewStates.choosing_shop)

    return await callback.message.answer(
        choose_shop(),
        reply_markup=get_shops_keyboard(shops)
    )


# =========================================================
# 🏪 SHOP
# =========================================================

@router.callback_query(F.data.startswith("shop_"))
async def handle_choose_shop(callback: CallbackQuery, state: FSMContext) -> Message:
    await callback.answer()

    shop_id = int(callback.data.split("_")[-1])
    await state.update_data(shop_id=shop_id)
    await state.set_state(ReviewStates.choosing_date)

    return await callback.message.answer(
        "📅 Выберите дату посещения\n\n"
        "Можно оставить отзыв только за последние 30 дней.",
        reply_markup=get_calendar_keyboard(page="current")
    )


# =========================================================
# 📅 КАЛЕНДАРЬ — НАВИГАЦИЯ
# =========================================================

@router.callback_query(
    ReviewStates.choosing_date,
    F.data.startswith("calendar_nav_")
)
async def handle_calendar_navigation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    page = callback.data.replace("calendar_nav_", "")
    await callback.message.delete()

    return await callback.message.answer(
        "📅 Выберите дату посещения\n\n"
        "Можно оставить отзыв только за последние 30 дней.",
        reply_markup=get_calendar_keyboard(page=page)
    )


# =========================================================
# 📅 КАЛЕНДАРЬ — ВЫБОР ДАТЫ
# =========================================================

@router.callback_query(
    ReviewStates.choosing_date,
    F.data.regexp(r"^calendar_\d{4}-\d{2}-\d{2}$")
)
async def handle_calendar_date(callback: CallbackQuery, state: FSMContext) -> Message:
    await callback.answer()

    tz = ZoneInfo("Asia/Irkutsk")
    today = datetime.now(tz).date()
    min_date = today - timedelta(days=30)

    date_str = callback.data.replace("calendar_", "")
    visit_date = datetime.fromisoformat(date_str).date()

    if visit_date > today or visit_date < min_date:
        return await callback.message.answer("⚠️ Нельзя выбрать эту дату.")

    await state.update_data(visit_date=visit_date)
    await state.set_state(ReviewStates.rating_taste)

    return await callback.message.answer(
        rate_taste(),
        reply_markup=get_rating_keyboard("taste")
    )


# =========================================================
# ⭐ RATINGS
# =========================================================

async def process_rating(
    callback: CallbackQuery,
    state: FSMContext,
    field: str,
    next_text: str,
    next_prefix: str,
    next_state
) -> Message:

    await callback.answer()

    value = int(callback.data.split("_")[-1])
    await state.update_data(**{field: value})
    await state.set_state(next_state)

    return await callback.message.answer(
        next_text,
        reply_markup=get_rating_keyboard(next_prefix)
    )


@router.callback_query(ReviewStates.rating_taste, F.data.startswith("taste_"))
async def process_taste(callback: CallbackQuery, state: FSMContext):
    return await process_rating(
        callback, state,
        "taste",
        rate_staff(),
        "staff",
        ReviewStates.rating_staff
    )


@router.callback_query(ReviewStates.rating_staff, F.data.startswith("staff_"))
async def process_staff(callback: CallbackQuery, state: FSMContext):
    return await process_rating(
        callback, state,
        "staff",
        rate_cleanliness(),
        "cleanliness",
        ReviewStates.rating_cleanliness
    )


@router.callback_query(ReviewStates.rating_cleanliness, F.data.startswith("cleanliness_"))
async def process_cleanliness(callback: CallbackQuery, state: FSMContext):
    return await process_rating(
        callback, state,
        "cleanliness",
        rate_speed(),
        "speed",
        ReviewStates.rating_speed
    )


@router.callback_query(ReviewStates.rating_speed, F.data.startswith("speed_"))
async def process_speed(callback: CallbackQuery, state: FSMContext):
    return await process_rating(
        callback, state,
        "speed",
        rate_price_value(),
        "price_value",
        ReviewStates.rating_price_value
    )


# =========================================================
# 💬 COMMENT
# =========================================================

@router.callback_query(
    ReviewStates.rating_price_value,
    F.data.startswith("price_value_")
)
async def process_price(callback: CallbackQuery, state: FSMContext) -> Message:
    await callback.answer()

    value = int(callback.data.split("_")[-1])
    await state.update_data(price_value=value)
    await state.set_state(ReviewStates.comment)

    return await callback.message.answer(
        ask_comment(),
        reply_markup=skip_keyboard("comment")
    )


@router.message(ReviewStates.comment)
async def process_comment(message: Message, state: FSMContext) -> Message:
    await state.update_data(comment=message.text)
    await state.set_state(ReviewStates.improvement)

    return await message.answer(
        ask_improvement(),
        reply_markup=skip_keyboard("improvement")
    )


@router.callback_query(ReviewStates.comment, F.data == "skip_comment")
async def skip_comment(callback: CallbackQuery, state: FSMContext) -> Message:
    await callback.answer()

    await state.update_data(comment=None)
    await state.set_state(ReviewStates.improvement)

    return await callback.message.answer(
        ask_improvement(),
        reply_markup=skip_keyboard("improvement")
    )


# =========================================================
# 💾 SAVE
# =========================================================

async def finalize_review(
    message: Message,
    state: FSMContext,
    telegram_id: int
) -> Message:

    data = await state.get_data()

    try:
        async with async_session() as session:
            review_repo = ReviewRepository(session)
            user_repo = UserRepository(session)

            user = await user_repo.get_or_create(
                telegram_id=telegram_id
            )

            service = ReviewService(review_repo)

            await service.create_full_review(
                user_id=user.id,
                shop_id=data["shop_id"],
                visit_date=data["visit_date"],
                ratings={
                    "taste": data["taste"],
                    "staff": data["staff"],
                    "cleanliness": data["cleanliness"],
                    "speed": data["speed"],
                    "price_value": data["price_value"],
                },
                comment=data.get("comment"),
                improvement=data.get("improvement"),
            )

    except ValueError as e:
        await state.clear()
        return await message.answer(f"⚠️ {str(e)}")

    await state.clear()

    return await message.answer("✅ Спасибо! Отзыв сохранён ☕")


# =========================================================
# 🛠 IMPROVEMENT
# =========================================================

@router.message(ReviewStates.improvement)
async def process_improvement(message: Message, state: FSMContext):
    await state.update_data(improvement=message.text)
    return await finalize_review(message, state, message.from_user.id)


@router.callback_query(ReviewStates.improvement, F.data == "skip_improvement")
async def skip_improvement(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(improvement=None)
    return await finalize_review(
        callback.message,
        state,
        callback.from_user.id
    )