from django.urls import path, include
from . import views

app_name = 'assignment'

urlpatterns = [
    path('create/', views.AssignmentCreate.as_view(), name='create-assignment'),
    path('mark/add/', views.AssignmentMarkCreate.as_view(), name='add-assignment-mark'),
    path('mail/send/', views.simple_mail, name='send-mail')
]
