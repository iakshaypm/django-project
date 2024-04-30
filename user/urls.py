from django.urls import path, include
from user import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'user'

urlpatterns = [
    path('account/register/', views.RegisterView.as_view(), name='user-register'),
    path('account/student/register/', views.StudentRegister.as_view(), name='student-register'),
    path('account/teacher/register/', views.TeacherRegister.as_view(), name='teacher-register'),
    path('account/hod/register/', views.HODRegister.as_view(), name='teacher-register'),
    path('account/login/', TokenObtainPairView.as_view(), name='login'),
    path('account/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('student/<int:id>/details/', views.UserView.as_view(), name='student-details'),
]
