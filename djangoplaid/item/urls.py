from django.urls import path
from . import views

app_name = 'item'
urlpatterns = [
    path('', views.link_form, name='link_form'),
    path('get_access_token/', views.get_access_token, name='get_access_token'),
    path('items/', views.institution_list, name='institution_list'),
    path('items/<int:item_id>/accounts/', views.account_list, name='item_account_list'),
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/<int:account_id>/', views.account_detail, name='account_detail'),
    path('accounts/transaction_stats/', views.account_statistic_form, name='accounts_stats')
]
