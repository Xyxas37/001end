from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from core.models import Transaction, UserProfile, Category
from datetime import date

router = Router()

class AddTransaction(StatesGroup):
    type = State()
    amount = State()
    category = State()
    date = State()
    description = State()

@router.message(Command("add"))
async def add_transaction_start(message: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Доход")], [KeyboardButton(text="Расход")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите тип операции:", reply_markup=kb)
    await state.set_state(AddTransaction.type)

@router.message(AddTransaction.type)
async def process_type(message: Message, state: FSMContext):
    text = message.text.lower()
    if text not in ["доход", "расход"]:
        await message.answer("Пожалуйста, выберите 'Доход' или 'Расход'")
        return

    await state.update_data(type="income" if text == "доход" else "expense")
    await message.answer("Введите сумму операции:", reply_markup=None)
    await state.set_state(AddTransaction.amount)

@router.message(AddTransaction.amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму.")
        return

    await state.update_data(amount=amount)

    telegram_id = message.from_user.id
    profile = UserProfile.objects.get(telegram_id=telegram_id)
    user = profile.user

    categories = Category.objects.filter(user=user)
    if not categories.exists():
        await message.answer("У вас нет категорий. Добавьте их через сайт.")
        await state.clear()
        return

    keyboard = [[KeyboardButton(text=cat.name)] for cat in categories]
    kb = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

    await message.answer("Выберите категорию:", reply_markup=kb)
    await state.set_state(AddTransaction.category)

@router.message(AddTransaction.category)
async def process_category(message: Message, state: FSMContext):
    category_name = message.text.strip()
    telegram_id = message.from_user.id
    profile = UserProfile.objects.get(telegram_id=telegram_id)
    user = profile.user

    try:
        category = Category.objects.get(name=category_name, user=user)
    except Category.DoesNotExist:
        await message.answer("Категория не найдена. Выберите из списка.")
        return

    await state.update_data(category_id=category.id)
    await message.answer("Введите день месяца (например, 5) или напишите 'сегодня':", reply_markup=None)
    await state.set_state(AddTransaction.date)

@router.message(AddTransaction.date)
async def process_date(message: Message, state: FSMContext):
    text = message.text.strip().lower()
    today = date.today()

    if text == "сегодня":
        selected_date = today
    else:
        try:
            day = int(text)
            selected_date = date(today.year, today.month, day)
        except ValueError:
            await message.answer("Введите число (1–31) или 'сегодня'")
            return
        except Exception:
            await message.answer("Такого дня нет в этом месяце.")
            return

    await state.update_data(date=selected_date)
    await message.answer("Введите описание или '-' для пропуска:")
    await state.set_state(AddTransaction.description)

@router.message(AddTransaction.description)
async def process_description(message: Message, state: FSMContext):
    description = message.text.strip()
    if description == "-":
        description = ""

    data = await state.get_data()
    profile = UserProfile.objects.get(telegram_id=message.from_user.id)
    user = profile.user
    category = Category.objects.get(id=data["category_id"])

    Transaction.objects.create(
        user=user,
        amount=data["amount"],
        type=data["type"],
        category=category,
        date=data["date"],
        description=description
    )

    await message.answer("✅ Транзакция добавлена!")
    await state.clear()
