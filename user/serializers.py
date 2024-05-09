from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from .models import Student, Teacher, HOD, Account
from grade.models import Mark
from classroom.models import Classroom
from attendance.models import StudentAttendance
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
    # user = serializers.IntegerField(write_only=True)
    # classroom = serializers.IntegerField(write_only=True)

    class Meta:
        model = Student
        fields = ['department', 'location', 'date_of_birth', 'user', 'classroom', 'parent']

    def validate(self, attrs):
        user = attrs['user']
        print(user)
        if user.user_type == 1:
            return attrs
        raise serializers.ValidationError({'user': 'Given user is not a student.'})


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['department', 'subject', 'user', 'classroom']

    def validate(self, attrs):
        user = attrs['user']
        if user.user_type == 2:
            return attrs
        raise serializers.ValidationError({'user': 'Given user is not a teacher.'})


class HODSerializer(serializers.ModelSerializer):
    class Meta:
        model = HOD
        fields = ['department', 'user']

    def validate(self, attrs):
        user = attrs['user']
        if user.user_type == 3:
            return attrs
        raise serializers.ValidationError({'user': 'Given user is not a HOD.'})


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['name']


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = ['sub1', 'sub2', 'sub3']


class StudentAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = ['date_of_marking']


class StudentViewSerializer(serializers.ModelSerializer):
    mark = MarkSerializer(read_only=True, source='student_mark', many=True)
    attendance = StudentAttendanceSerializer(read_only=True, source='student_attendance', many=True)
    student = StudentSerializer(read_only=True)
    classroom = ClassroomSerializer(source='student.classroom', read_only=True)

    class Meta:
        model = Account
        fields = ['name', 'student', 'classroom', 'attendance', 'mark']
