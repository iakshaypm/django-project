from django.urls import path, include
from exam import views

app_name = 'exam'

urlpatterns = [
    path('add/', views.ExamCreateView.as_view(), name='create-question'),
]
