from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializer import AttendanceSerializer, StudentAttendanceSerializer, TeacherAttendanceSerializer
from .permission import CanAddAttendance, IsStudent, CanMarkAttendance, IsTeacher
from .models import MainAttendance


class AttendanceCreateView(generics.CreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = (IsAuthenticated, CanAddAttendance, )

    def post(self, request, *args, **kwargs):
        message = ''
        ATTENDANCE_TYPE_CHOOSES = {
            'Student': 1,
            'Teacher': 2,
            'HOD': 3
        }
        serializer = AttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(initiated_by=request.user)
        for key, value in ATTENDANCE_TYPE_CHOOSES.items():
            if value == request.data['attendance_type']:
                message = key + ' attendance created successfully'
        return Response({
            'status': status.HTTP_200_OK,
            'message': message,
            'data': serializer.data
        })


class ShowAttendanceView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return MainAttendance.objects.all().filter(attendance_type=self.request.user.user_type)


class StudentAttendanceCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, CanMarkAttendance, IsStudent,)

    def post(self, request, *args, **kwargs):
        serializer = StudentAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(student=request.user)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Marked attendance successfully.',
            'data': serializer.data
        })


class TeacherAttendanceCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, CanMarkAttendance, IsTeacher, )

    def post(self, request, *args, **kwargs):
        serializer = TeacherAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(teacher=request.user)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Marked attendance successfully.',
            'data': serializer.data
        })
