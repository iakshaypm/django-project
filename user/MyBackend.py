from django.contrib.auth.backends import BaseBackend, ModelBackend
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from .models import Account


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Account.objects.filter(
                Q(email=username) | Q(phone_number=username)
            ).first()
            if user.check_password(password):
                return user
        except Account.DoesNotExist:
            return Response({'msg': 'Login Success'}, status=status.HTTP_200_OK)

    def get_user(self, user_id):
        try:
            return Account.objects.get(pk=user_id)
        except Account.DoesNotExist:
            return None

    def get_user_by_username(self, username):
        try:
            return Account.objects.get(
                Q(email=username) | Q(phone_number=username)
            )
        except Account.DoesNotExist:
            return None
