import os
import django
import asyncio
from datetime import timedelta, date

from apscheduler.schedulers.background import BackgroundScheduler
from core.models import UserProfile, Transaction, UserCategoryLimit
from bot.config import bot, dp
from bot.handlers import base_router, add_router, stats_router, setlimit_router

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fincontrol.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

scheduler = BackgroundScheduler()


def check_category_limits(user, transactions):
    category_totals = {}
    for t in transactions:
        if t.type != "expense":
            continue
        category_totals[t.category.name] = category_totals.get(t.category.name, 0) + float(t.amount)

    limits = UserCategoryLimit.objects.filter(user=user, limit_type="day")  # только дневные лимиты

    message = ""
    for limit in limits:
        category_name = limit.category.name
        total = category_totals.get(category_name, 0)
        if total > float(limit.limit):
            message += (
                f"⚠️ Лимит для категории «{category_name}» "
                f"({limit.get_limit_type_display()}) превышен на {total - float(limit.limit):,.2f} ₽\n"
            )
    return message


def send_daily_report():
    users = UserProfile.objects.all()
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())

    for profile in users:
        user = profile.user
        telegram_id = profile.telegram_id

        daily_transactions = Transaction.objects.filter(user=user, date=today)
        weekly_transactions = Transaction.objects.filter(user=user, date__gte=start_of_week)

        daily_income = sum(float(t.amount) for t in daily_transactions if t.type == "income")
        daily_expense = sum(float(t.amount) for t in daily_transactions if t.type == "expense")
        weekly_income = sum(float(t.amount) for t in weekly_transactions if t.type == "income")
        weekly_expense = sum(float(t.amount) for t in weekly_transactions if t.type == "expense")

        daily_balance = daily_income - daily_expense
        weekly_balance = weekly_income - weekly_expense

        message = (
            f"📊 <b>Ежедневный отчёт</b>\n\n"
            f"📅 <b>Сегодня:</b>\n"
            f"💰 Доход: {daily_income:,.2f} ₽\n"
            f"💸 Расход: {daily_expense:,.2f} ₽\n"
            f"📊 Баланс: {daily_balance:,.2f} ₽\n\n"
            f"📅 <b>За неделю:</b>\n"
            f"💰 Доход: {weekly_income:,.2f} ₽\n"
            f"💸 Расход: {weekly_expense:,.2f} ₽\n"
            f"📊 Баланс: {weekly_balance:,.2f} ₽"
        )

        category_warning = check_category_limits(user, daily_transactions)
        if category_warning:
            message += f"\n\n{category_warning}"

        bot.send_message(telegram_id, message, parse_mode="HTML")

    print("✅ Ежедневный отчёт отправлен.")


scheduler.add_job(send_daily_report, 'interval', hours=24)


def send_weekly_report():
    users = UserProfile.objects.all()
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())

    for profile in users:
        user = profile.user
        telegram_id = profile.telegram_id

        weekly_transactions = Transaction.objects.filter(user=user, date__gte=start_of_week)

        weekly_income = sum(float(t.amount) for t in weekly_transactions if t.type == "income")
        weekly_expense = sum(float(t.amount) for t in weekly_transactions if t.type == "expense")
        weekly_balance = weekly_income - weekly_expense

        message = (
            f"📊 <b>Еженедельный отчёт</b>\n\n"
            f"📅 <b>За неделю:</b>\n"
            f"💰 Доход: {weekly_income:,.2f} ₽\n"
            f"💸 Расход: {weekly_expense:,.2f} ₽\n"
            f"📊 Баланс: {weekly_balance:,.2f} ₽"
        )

        bot.send_message(telegram_id, message, parse_mode="HTML")

    print("✅ Еженедельный отчёт отправлен.")


scheduler.add_job(send_weekly_report, 'interval', weeks=1, days=0, hours=0, minutes=0)


def start_scheduler():
    scheduler.start()


async def main():
    dp.include_router(base_router)
    dp.include_router(add_router)
    dp.include_router(stats_router)
    dp.include_router(setlimit_router)
    start_scheduler()
    print("✅ Бот запущен")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
