from reportlab.pdfgen import canvas

from django.core import serializers

import json

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from .permission import IsTeacher, IsStudent, IsHOD, IsManagement, IsParent
from .models import Account, Student

from grade.models import Mark
from grade.serializer import MarkSerializer

from attendance.models import StudentAttendance

from user.serializers import (UserSerializer, StudentSerializer, TeacherSerializer, HODSerializer,
                              StudentViewSerializer, )
from celery import shared_task

import urllib

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views import View
from django.conf import settings
from django.shortcuts import redirect
import requests


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


class StripeAuthorizeView(View):

    def get(self, request):
        # if not self.request.user.is_authenticated:
        #     return HttpResponseRedirect(reverse('login'))
        url = 'https://connect.stripe.com/oauth/authorize'
        params = {
            'response_type': 'code',
            'scope': 'read_write',
            'client_id': settings.STRIPE_CONNECT_CLIENT_ID,
            'redirect_uri': f'http://localhost:8000/users/oauth/callback'
        }
        url = f'{url}?{urllib.parse.urlencode(params)}'
        return redirect(url)


class StripeAuthorizeCallbackView(View):

    def get(self, request):
        code = request.GET.get('code')
        if code:
            data = {
                'client_secret': settings.STRIPE_SECRET_KEY,
                'grant_type': 'authorization_code',
                'client_id': settings.STRIPE_CONNECT_CLIENT_ID,
                'code': code
            }
            url = 'https://connect.stripe.com/oauth/token'
            resp = requests.post(url, params=data)
            print(resp.json())
        # url = reverse('home')
        # response = resp.json()
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Fetched student detail successfully',
        })
