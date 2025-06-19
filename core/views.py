from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Transaction, Category
from .forms import TransactionForm
from .forms import CategoryLimitForm
from .models import UserCategoryLimit
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout

from datetime import datetime

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'core/transaction_list.html', {'transactions': transactions})


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'core/add_transaction.html', {'form': form})


@login_required
def dashboard_view(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by("-date")

    # Фильтрация
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    category = request.GET.get("category")
    tx_type = request.GET.get("type")

    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
    if category and category != "all":
        transactions = transactions.filter(category__id=category)
    if tx_type and tx_type in ["income", "expense"]:
        transactions = transactions.filter(type=tx_type)

    categories = Category.objects.filter(user=user)

    context = {
        "transactions": transactions,
        "categories": categories,
        "filters": {
            "date_from": date_from,
            "date_to": date_to,
            "category": category,
            "type": tx_type,
        },
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def set_category_limit(request):
    if request.method == 'POST':
        form = CategoryLimitForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            limit_type = form.cleaned_data['limit_type']
            limit = form.cleaned_data['limit']

            # Проверка: существует ли уже лимит
            existing = UserCategoryLimit.objects.filter(
                user=request.user,
                category=category,
                limit_type=limit_type
            ).first()

            if existing:
                existing.limit = limit
                existing.save()
            else:
                limit_obj = form.save(commit=False)
                limit_obj.user = request.user
                limit_obj.save()

            return redirect('dashboard')
    else:
        form = CategoryLimitForm()

    return render(request, 'core/set_category_limit.html', {'form': form})

@login_required
def my_limits(request):
    limits = UserCategoryLimit.objects.filter(user=request.user).select_related('category')
    return render(request, 'core/my_limits.html', {'limits': limits})

@login_required
def delete_limit(request, limit_id):
    limit = get_object_or_404(UserCategoryLimit, id=limit_id, user=request.user)
    limit.delete()
    return redirect('my_limits')


@login_required
def edit_limit(request, limit_id):
    limit = get_object_or_404(UserCategoryLimit, id=limit_id, user=request.user)
    if request.method == 'POST':
        form = CategoryLimitForm(request.POST, instance=limit)
        if form.is_valid():
            form.save()
            return redirect('my_limits')
    else:
        form = CategoryLimitForm(instance=limit)
    return render(request, 'core/edit_limit.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('transaction_list')

@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(user=request.user, name=name)
            return redirect('category_list')
    return render(request, 'core/add_category.html')

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'core/category_list.html', {'categories': categories})

@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    category.delete()
    return redirect('category_list')
