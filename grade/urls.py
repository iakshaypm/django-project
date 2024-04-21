from django.urls import path, include
from grade import views

app_name = 'grade'

urlpatterns = [
    path('add/', views.MarkCreateView.as_view(), name='add-mark'),
    path('show/', views.MarkListView.as_view(), name='show-mark'),
    path('<int:pk>/delete/', views.MarkDeleteView.as_view(), name='delete-mark'),
]
