from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from core.models import UserProfile, Transaction
from analytics.plot_weekly import build_weekly_plot
from analytics.plot_categories import build_category_pie
from datetime import date, timedelta
from analytics.advice import generate_weekly_advice

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    telegram_id = message.from_user.id
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        user = profile.user
    except UserProfile.DoesNotExist:
        await message.answer("Вы ещё не зарегистрированы. Используйте /start.")
        return

    path = build_weekly_plot(user)
    if not path:
        await message.answer("Недостаточно данных для построения графика.")
        return

    photo = FSInputFile(path)
    await message.answer_photo(photo, caption="📊 Ваши расходы за последние 7 дней")


@router.message(Command("categories"))
async def cmd_categories(message: Message):
    telegram_id = message.from_user.id
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        user = profile.user
    except UserProfile.DoesNotExist:
        await message.answer("Вы не зарегистрированы. Используйте /start.")
        return

    path = build_category_pie(user)
    if not path:
        await message.answer("Недостаточно данных для построения диаграммы.")
        return

    photo = FSInputFile(path)
    await message.answer_photo(photo, caption="📊 Расходы по категориям за 7 дней")

@router.message(Command("summary"))
async def cmd_summary(message: Message):
    telegram_id = message.from_user.id
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        user = profile.user
    except UserProfile.DoesNotExist:
        await message.answer("Вы не зарегистрированы. Используйте /start.")
        return

    today = date.today()
    start_date = today - timedelta(days=7)

    transactions = Transaction.objects.filter(user=user, date__gte=start_date)

    income = sum(float(t.amount) for t in transactions if t.type == "income")
    expense = sum(float(t.amount) for t in transactions if t.type == "expense")
    balance = income - expense

    text = (
        f"📋 <b>Сводка за неделю</b>:\n\n"
        f"💰 Доход: {income:,.0f} ₽\n"
        f"💸 Расход: {expense:,.0f} ₽\n"
        f"📊 Баланс: {'+' if balance >= 0 else ''}{balance:,.0f} ₽"
    )

    await message.answer(text, parse_mode="HTML")


@router.message(Command("advise"))
async def cmd_advise(message: Message):
    telegram_id = message.from_user.id
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        user = profile.user
    except UserProfile.DoesNotExist:
        await message.answer("Вы не зарегистрированы. Используйте /start.")
        return

    text = generate_weekly_advice(user)
    await message.answer(f"📊 Рекомендации:\n\n{text}")


