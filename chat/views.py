from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.permissions import IsAuthenticated

from .models import Room
from .serializers import RoomSerializer
from .permission import CanCreateRoom


# Create your views here.
@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def index_view(request):
    return Response({
        'rooms': Room.objects.all(),
    })


class CreateRoomView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, CanCreateRoom)

    def post(self, request, *args, **kwargs):
        serializer = RoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Student room created successfully.',
            'data': serializer.data
        })

