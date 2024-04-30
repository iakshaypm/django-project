from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from user.models import Account, Student
from classroom.models import Classroom
from attendance.models import MainAttendance
from django.contrib.auth import get_user_model
from rest_framework import status
import datetime

login_url = reverse('user:login')
main_attendance_url = reverse('attendance:add-attendance')
mark_student_attendance = reverse('attendance:mark-student-attendance')


# from app.models import MyModel
class TestMainAttendance(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.teacher = get_user_model().objects.create_user(
            email="teacher4@example.com",
            password="Test123",
            phone_number="7990999959",
            name="Teacher 4",
            user_type=2
        )
        self.access_token_teacher = AccessToken.for_user(self.teacher)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token_teacher}')

        self.classroom = Classroom.objects.create(
            name="Classroom 1",
            total_strength=50
        )
        self.student = get_user_model().objects.create_user(
            email="student@example.com",
            password="Test123",
            phone_number="79970999959",
            name="Student",
            user_type=1
        )
        Student.objects.create(
            department="CS",
            location="TVM",
            date_of_birth="2000-03-06",
            user=self.student,
            classroom=self.classroom
        )

        self.access_token_student = AccessToken.for_user(self.student)

    def test_creating_main_attendance(self):
        data = {
            "attendance_type": 1,
            "classroom": self.classroom.id
        }
        response = self.client.post(main_attendance_url, data, format='json')
        self.attendance_id = response.data['data']['id']
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_adding_student_attendance(self):
        data = {
            "attendance_type": 1,
            "classroom": self.classroom.id
        }
        response = self.client.post(main_attendance_url, data, format='json')
        self.attendance_id = response.data['data']['id']
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token_student}')
        data = {
            "attendance": 1
        }
        response = self.client.post(mark_student_attendance, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
