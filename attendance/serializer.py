from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import MainAttendance, StudentAttendance, TeacherAttendance
from user.models import Account


class AttendanceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    initiated_by = serializers.CharField(read_only=True)
    date_of_producing = serializers.DateField(read_only=True)

    class Meta:
        model = MainAttendance
        fields = ['id', 'attendance_type', 'initiated_by', 'classroom', 'date_of_producing']


class StudentAttendanceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    student = serializers.CharField(read_only=True)
    date_of_marking = serializers.DateField(read_only=True)

    class Meta:
        model = StudentAttendance
        fields = ['id', 'attendance', 'student', 'date_of_marking']

    def validate_attendance_id(self, value):
        if not MainAttendance.objects.filter(id=value).exists():
            raise serializers.ValidationError("id doesn't belongs to a valid attendance.")
        return value


class TeacherAttendanceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    teacher = serializers.CharField(read_only=True)
    date_of_marking = serializers.DateField(read_only=True)

    class Meta:
        model = TeacherAttendance
        fields = ['id', 'attendance', 'teacher', 'date_of_marking']

    def validate_attendance_id(self, value):
        if not MainAttendance.objects.filter(id=value).exists():
            raise serializers.ValidationError("id doesn't belongs to a valid attendance.")
        return value
