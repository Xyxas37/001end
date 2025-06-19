from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'
    TYPE_CHOICES = [
        (INCOME, 'Доход'),
        (EXPENSE, 'Расход'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_type_display()} — {self.amount} ({self.date})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.BigIntegerField(unique=True)

    def __str__(self):
        return f"{self.user.username} ({self.telegram_id})"

class UserCategoryLimit(models.Model):
    LIMIT_TYPE_CHOICES = [
        ('day', 'День'),
        ('week', 'Неделя'),
        ('month', 'Месяц'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    limit_type = models.CharField(max_length=10, choices=LIMIT_TYPE_CHOICES)
    limit = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('user', 'category', 'limit_type')

    def __str__(self):
        return f"{self.user.username} - {self.category.name} ({self.get_limit_type_display()}): {self.limit} ₽"


@receiver(post_save, sender=UserCategoryLimit)
def notify_user_on_limit_set(sender, instance, created, **kwargs):
    if created:
        import asyncio
        import os
        from aiogram import Bot
        from dotenv import load_dotenv

        load_dotenv()
        bot = Bot(token=os.getenv("BOT_TOKEN"))

        user = instance.user
        telegram_id = user.userprofile.telegram_id
        message = f"🔔 Ваш лимит для категории '{instance.category.name}' установлен на {instance.limit} ₽ ({instance.get_limit_type_display()})."


        asyncio.run(bot.send_message(telegram_id, message))

