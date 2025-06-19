from django.urls import path
from . import views
from .views import (set_category_limit, my_limits, delete_limit, edit_limit, logout_view, add_category, category_list, delete_category, )

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('set-limit/', set_category_limit, name='set_category_limit'),
    path('my-limits/', my_limits, name='my_limits'),
    path('delete-limit/<int:limit_id>/', delete_limit, name='delete_limit'),
    path('edit-limit/<int:limit_id>/', edit_limit, name='edit_limit'),
    path('logout/', logout_view, name='logout'),
    path('add-category/', add_category, name='add_category'),
    path('categories/', category_list, name='category_list'),
    path('delete-category/<int:category_id>/', delete_category, name='delete_category'),

]
