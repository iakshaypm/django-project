from django.urls import path, include
from user import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
]

