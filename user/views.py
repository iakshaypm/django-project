from reportlab.pdfgen import canvas

from django.core import serializers

import json

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from .permission import IsTeacher, IsStudent, IsHOD, IsManagement
from .models import Account, Student

from grade.models import Mark
from grade.serializer import MarkSerializer

from attendance.models import StudentAttendance

from user.serializers import (UserSerializer, StudentSerializer, TeacherSerializer, HODSerializer,
                              StudentViewSerializer, )
from celery import shared_task


class RegisterView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'User created successfully',
            'data': serializer.data
        })


class StudentRegister(views.APIView):
    permission_classes = (IsAuthenticated, IsTeacher | IsManagement)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Student added successfully',
            'data': serializer.data
        })


class TeacherRegister(views.APIView):
    permission_classes = (IsAuthenticated, IsHOD | IsManagement,)

    def post(self, request):
        serializer = TeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Teacher added successfully',
            'data': serializer.data
        })


class HODRegister(views.APIView):
    permission_classes = (IsAuthenticated, IsManagement)

    def post(self, request):
        serializer = HODSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'HOD added successfully',
            'data': serializer.data
        })


class UserView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        self.generate_pdf.delay(kwargs['id'])
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Fetched student detail successfully',
        })

    @shared_task(bind=True)
    def generate_pdf(self, id):
        user = Account.objects.get(id=id)
        serializer = StudentViewSerializer(user)
        data = json.dumps(serializer.data)
        p = canvas.Canvas('report_' + user.name.lower() + '.pdf')

        p.drawString(100, 700, data)

        p.showPage()
        p.save()
