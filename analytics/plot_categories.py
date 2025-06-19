import plotly.graph_objects as go
from datetime import timedelta, date
from core.models import Transaction

def build_category_pie(user):
    today = date.today()
    start_date = today - timedelta(days=6)

    transactions = Transaction.objects.filter(
        user=user,
        type='expense',
        date__range=(start_date, today)
    )

    if not transactions.exists():
        return None

    data = {}
    for t in transactions:
        name = t.category.name
        data[name] = data.get(name, 0) + float(t.amount)

    labels = list(data.keys())
    values = list(data.values())

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
    fig.update_layout(title="Расходы по категориям (7 дней)", template="plotly_white")

    path = "analytics/pie_categories.png"
    fig.write_image(path)
    return path
