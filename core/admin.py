from django.contrib import admin
from .models import Category, Transaction, UserProfile

admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(UserProfile)