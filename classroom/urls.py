from django.urls import path, include
from classroom import views

app_name = 'classroom'

urlpatterns = [
    path('add/', views.ClassroomCreateView.as_view(), name='add-classroom'),
    path('show/', views.ClassroomListView.as_view(), name='show-classroom'),
]
