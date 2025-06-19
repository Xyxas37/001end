from datetime import date, timedelta
from core.models import Transaction

def generate_weekly_advice(user):
    today = date.today()
    start_date = today - timedelta(days=7)

    transactions = Transaction.objects.filter(user=user, date__gte=start_date)

    if not transactions.exists():
        return "Недостаточно данных для анализа."

    advice_lines = []

    # Общий расход
    total_expense = sum(float(t.amount) for t in transactions if t.type == "expense")
    if total_expense > 10000:
        advice_lines.append("⚠️ Ваши расходы за неделю превысили 10 000 ₽")

    # Расходы по категориям
    category_totals = {}
    for t in transactions:
        if t.type != "expense":
            continue
        cat = t.category.name
        category_totals[cat] = category_totals.get(cat, 0) + float(t.amount)

    for cat, amount in category_totals.items():
        if amount > 3000:
            advice_lines.append(f"💡 Вы потратили на {cat} {amount:.0f} ₽ за неделю — это выше среднего.")

    if not advice_lines:
        return "✅ Всё стабильно. Расходы под контролем."

    return "\n".join(advice_lines)
