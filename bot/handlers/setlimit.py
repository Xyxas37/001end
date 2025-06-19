from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from core.models import UserProfile, Category, UserCategoryLimit
import logging

router = Router()

logging.basicConfig(level=logging.DEBUG)

@router.message(Command("setlimit"))
async def cmd_setlimit(message: Message, state: FSMContext):
    logging.debug(f"Received /setlimit command from {message.from_user.id}")

    # Запрашиваем категорию
    await message.answer("Введите категорию для установки лимита:")
    await state.set_state("waiting_for_category")
    logging.debug("Waiting for category...")


@router.message(State("waiting_for_category"))
async def process_category(message: Message, state: FSMContext):
    category_name = message.text.strip()
    logging.debug(f"Received category input: {category_name}")


    try:
        category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        await message.answer("Категория не найдена. Попробуйте снова.")
        logging.debug(f"Category '{category_name}' not found.")
        return


    await state.update_data(category_id=category.id)
    logging.debug(f"Category '{category_name}' selected.")


    await message.answer(f"Вы выбрали категорию '{category_name}'. Теперь введите лимит:")
    await state.set_state("waiting_for_limit")  # Устанавливаем следующее состояние
    logging.debug("Waiting for limit...")


@router.message(State("waiting_for_limit"))
async def process_limit(message: Message, state: FSMContext):
    limit_text = message.text.strip()
    logging.debug(f"Received limit input: {limit_text}")

    try:
         limit = float(limit_text)
    except ValueError:
        await message.answer("Некорректный лимит. Пожалуйста, введите корректное число.")
        return

    data = await state.get_data()
    category = Category.objects.get(id=data["category_id"])
    user_profile = UserProfile.objects.get(telegram_id=message.from_user.id)

    user_limit, created = UserCategoryLimit.objects.get_or_create(
        user=user_profile.user, category=category
    )
    user_limit.limit = limit
    user_limit.save()

    logging.debug(f"Limit set for category '{category.name}' to {limit}")

    await message.answer(f"Лимит для категории '{category.name}' установлен на {limit} ₽.")


    await state.clear()
    logging.debug(f"State cleared. Limiting process finished.")
