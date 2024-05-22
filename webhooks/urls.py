from django.urls import path

from . import views

app_name = "webhooks"

urlpatterns = [
    path("chat/", views.TelegramWebhook.as_view(), name="telegram_webhook")
]