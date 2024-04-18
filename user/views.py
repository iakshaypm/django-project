from rest_framework import views, status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permission import IsTeacher
from .models import Account

from user.serializers import UserSerializer, StudentSerializer


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
    permission_classes = (IsAuthenticated, IsTeacher,)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Student created successfully',
            'data': serializer.data
        })
