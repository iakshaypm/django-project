from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.auth, name='auth'),
    path('callback/', views.callback, name='callback'),
    path('refresh-token/', views.get_new_access_token, name='refresh-token'),
    path('profile/', views.get_user_profile, name='hubspot_profile'),
    path('hubspot_users/', views.get_hubspot_users, name='hubspot_users'),
    path('companies/', views.get_companies, name='companies'),
    path('contacts/', views.get_contacts, name='contacts'),
    path('deals/', views.get_deals, name='deals'),
    path('list_items/', views.get_list_items, name='list_items'),
    path('products/', views.get_products, name='products'),
    path('webhook/', views.webhook_handler, name='webhook'),
    path('company_currency/', views.get_company_currency, name='company_currency'),
]
