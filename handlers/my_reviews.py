from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database.session import async_session
from repositories.review_repo import ReviewRepository
from repositories.user_repo import UserRepository

from keyboards.inline_reviews import (
    reviews_list_keyboard,
    review_detail_keyboard,
    confirm_delete_keyboard,
)

from utils.texts import my_reviews_title

router = Router()

REVIEWS_PER_PAGE = 3


# =====================================================
# 📋 Экран списка отзывов
# =====================================================
@router.callback_query(F.data == "my_reviews")
async def show_my_reviews(callback: CallbackQuery, state: FSMContext) -> Message:
    await callback.answer()

    async with async_session() as session:
        review_repo = ReviewRepository(session)
        user_repo = UserRepository(session)

        user = await user_repo.get_or_create(
            telegram_id=callback.from_user.id
        )

        visits = await review_repo.get_user_visits(user.id)

    if not visits:
        return await callback.message.answer("У вас пока нет отзывов.")

    await state.update_data(
        reviews_ids=[v.id for v in visits]
    )

    page = 0

    msg = await callback.message.answer(
        my_reviews_title(),
        reply_markup=reviews_list_keyboard(visits, page),
    )

    return msg


# =====================================================
# 🔁 Переключение страницы
# =====================================================
@router.callback_query(F.data.startswith("reviews_page:"))
async def change_reviews_page(callback: CallbackQuery, state: FSMContext) -> Message:
    await callback.answer()

    page = int(callback.data.split(":")[1])

    data = await state.get_data()
    review_ids = data.get("reviews_ids", [])

    if not review_ids:
        return await callback.message.answer("Нет данных.")

    async with async_session() as session:
        review_repo = ReviewRepository(session)

        visits = []
        for review_id in review_ids:
            visit = await review_repo.get_visit_with_details(review_id)
            if visit:
                visits.append(visit)

    msg = await callback.message.answer(
        my_reviews_title(),
        reply_markup=reviews_list_keyboard(visits, page),
    )

    return msg


# =====================================================
# 📄 Детали одного отзыва
# =====================================================
@router.callback_query(F.data.startswith("review_detail:"))
async def show_review_detail(callback: CallbackQuery) -> Message:
    await callback.answer()

    visit_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        review_repo = ReviewRepository(session)
        visit = await review_repo.get_visit_with_details(visit_id)

    if not visit:
        return await callback.message.answer("Отзыв не найден.")

    ratings_map = {r.criterion_key: r.rating for r in visit.ratings}

    text = (
        f"🏪 {visit.shop.name}\n"
        f"📅 {visit.visit_date}\n\n"
        f"⭐ Вкус: {ratings_map.get('taste', '-')}\n"
        f"🧑‍🍳 Персонал: {ratings_map.get('staff', '-')}\n"
        f"🧼 Чистота: {ratings_map.get('cleanliness', '-')}\n"
        f"⚡ Скорость: {ratings_map.get('speed', '-')}\n"
        f"💰 Цена/качество: {ratings_map.get('price_value', '-')}\n"
    )

    if visit.text:
        if visit.text.comment:
            text += f"\n💬 Комментарий: {visit.text.comment}\n"

        if visit.text.improvement_suggestion:
            text += f"\n🔧 Улучшить: {visit.text.improvement_suggestion}\n"

    msg = await callback.message.answer(
        text,
        reply_markup=review_detail_keyboard(visit.id),
    )

    return msg


# =====================================================
# ⚠️ Подтверждение удаления
# =====================================================
@router.callback_query(F.data.startswith("delete_review:"))
async def ask_delete_confirmation(callback: CallbackQuery) -> Message:
    await callback.answer()

    visit_id = int(callback.data.split(":")[1])

    msg = await callback.message.answer(
        "⚠ Вы уверены, что хотите удалить отзыв?",
        reply_markup=confirm_delete_keyboard(visit_id),
    )

    return msg


# =====================================================
# 🗑 Подтверждённое удаление
# =====================================================
@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete(callback: CallbackQuery, state: FSMContext) -> Message:
    await callback.answer()

    visit_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        review_repo = ReviewRepository(session)
        await review_repo.mark_deleted(visit_id)

        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(
            telegram_id=callback.from_user.id
        )

        visits = await review_repo.get_user_visits(user.id)

    if not visits:
        return await callback.message.answer("У вас пока нет отзывов.")

    await state.update_data(
        reviews_ids=[v.id for v in visits]
    )

    page = 0

    msg = await callback.message.answer(
        my_reviews_title(),
        reply_markup=reviews_list_keyboard(visits, page),
    )

    return msg
