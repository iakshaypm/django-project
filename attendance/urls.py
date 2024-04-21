from django.urls import path, include
from attendance import views

app_name = 'attendance'

urlpatterns = [
    path('add/', views.AttendanceCreateView.as_view(), name='add-attendance'),
    path('show/', views.ShowAttendanceView.as_view(), name='show-attendance'),

    path('student/mark/', views.StudentAttendanceCreateView.as_view(), name='mark-student-attendance'),
    path('teacher/mark/', views.TeacherAttendanceCreateView.as_view(), name='mark-teacher-attendance'),
]
