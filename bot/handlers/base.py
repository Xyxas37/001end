from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from core.models import Transaction, UserProfile
from django.contrib.auth.models import User
from datetime import date, timedelta
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    telegram_id = message.from_user.id
    try:
        UserProfile.objects.get(telegram_id=telegram_id)
        await message.answer("👋 Вы уже зарегистрированы!")
    except UserProfile.DoesNotExist:
        user = User.objects.create_user(username=f"user_{telegram_id}")
        UserProfile.objects.create(user=user, telegram_id=telegram_id)
        await message.answer("✅ Вы успешно зарегистрированы!")

    await message.answer(
        "Используй команды:\n"
        "/start – регистрация\n"
        "/help – список всех команд"
    )


@router.message(Command("today"))
async def cmd_today(message: Message):
    telegram_id = message.from_user.id
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        user = profile.user
    except UserProfile.DoesNotExist:
        await message.answer("Вы ещё не зарегистрированы. Используйте /start.")
        return

    today = date.today()
    transactions = Transaction.objects.filter(user=user, date=today)

    if not transactions:
        await message.answer("Сегодня у вас нет операций.")
        return

    text = "Сегодняшние операции:\n"
    for t in transactions:
        text += f"{t.get_type_display()} — {t.amount} ({t.category.name})\n"
    await message.answer(text)

@router.message(Command("week"))
async def cmd_week(message: Message):
    telegram_id = message.from_user.id
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        user = profile.user
    except UserProfile.DoesNotExist:
        await message.answer("Вы ещё не зарегистрированы. Используйте /start.")
        return

    start_date = date.today() - timedelta(days=7)
    transactions = Transaction.objects.filter(user=user, date__gte=start_date)

    if not transactions:
        await message.answer("За последнюю неделю операций не найдено.")
        return

    text = "Операции за неделю:\n"
    for t in transactions:
        text += f"{t.date}: {t.get_type_display()} — {t.amount} ({t.category.name})\n"
    await message.answer(text)

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "<b>FinControl — Telegram-бот учёта финансов</b>\n\n"
        "📌 <b>Основные команды:</b>\n"
        "/start — регистрация или проверка\n"
        "/add — добавить операцию\n"
        "/today — показать операции за сегодня\n"
        "/week — показать операции за неделю\n"
        "/summary — доход, расход, баланс за 7 дней\n"
        "/stats — график расходов по дням\n"
        "/categories — диаграмма расходов по категориям\n"
        "/setlimit — установить лимит для категории\n"
        "/help — список команд\n"
        "/cancel — отменить ввод (в любом месте)"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Ввод отменён. Вы можете начать заново, например с /add.")