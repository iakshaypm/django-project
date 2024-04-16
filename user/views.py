from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.views import LoginView

from user.serializers import UserSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class UserLoginView(views.APIView):

    def post(self, request):
        if 'username' not in request.data or 'password' not in request.data:
            return Response({'msg': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        username = request.data['username']
        password = request.data['password']
        # print(username, password)
        user = authenticate(request, username=username, password=password)

        return Response({'msg': 'Login Success'}, status=status.HTTP_200_OK)

