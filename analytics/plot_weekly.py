import plotly.graph_objects as go
from datetime import timedelta, date
from core.models import Transaction

def build_weekly_plot(user):
    today = date.today()
    start_date = today - timedelta(days=6)

    transactions = Transaction.objects.filter(
        user=user,
        type='expense',
        date__range=(start_date, today)
    )

    if not transactions.exists():
        return None

    data = {start_date + timedelta(days=i): 0 for i in range(7)}
    for t in transactions:
        data[t.date] += float(t.amount)

    x = [d.strftime("%d.%m") for d in data]
    y = list(data.values())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name='Расходы'))
    fig.update_layout(
        title="Расходы за 7 дней",
        xaxis_title="Дата",
        yaxis_title="Сумма",
        template="plotly_white"
    )

    path = "analytics/weekly_plot.png"
    fig.write_image(path)
    return path
