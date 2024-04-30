from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

from rest_framework import status


class AdminSiteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test User',
        )


class ModelTest(TestCase):
    def test_create_user_with_email_successful(self):

        email = 'test@example.com'
        password = 'testpass123'
        phone_number = '9999999999',
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            phone_number=phone_number,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))



