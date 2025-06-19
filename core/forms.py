from django import forms
from .models import UserCategoryLimit, Category, Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'date', 'type', 'category', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


    amount = forms.DecimalField(label="Сумма")
    type = forms.ChoiceField(label="Тип", choices=Transaction.TYPE_CHOICES)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Категория")
    description = forms.CharField(widget=forms.Textarea, label="Описание")

class CategoryLimitForm(forms.ModelForm):
    class Meta:
        model = UserCategoryLimit
        fields = ['category', 'limit_type', 'limit']

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Категория"
    )
    limit_type = forms.ChoiceField(
        choices=UserCategoryLimit.LIMIT_TYPE_CHOICES,
        label="Тип лимита"
    )
    limit = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Лимит"
    )

