from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from .models import Student

from rest_framework import serializers, exceptions


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        max_length=100, write_only=True, required=True
    )

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'confirm_password', 'phone_number', 'name', 'user_type', 'is_staff',
                  'is_superuser']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'confirm_password': {'write_only': True, 'min_length': 5}
        }

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return get_user_model().objects.create_user(**validated_data)

    def validate(self, attrs):
        if attrs.get('password') == attrs.get('confirm_password'):
            return attrs
        raise serializers.ValidationError({'confirm_password': 'Password is not same!'})


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['department', 'location', 'date_of_birth', 'user_id']
