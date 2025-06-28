from .models import Room
from .serializers import RoomSerializer, UserSerializer
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .deck import Deck


class CreateRoomView(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # print(dir(request))
        cards = Deck()
        cards.shuffle()
        serializer = RoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(cards=cards.deal(request.data['playerCount']))
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Room created successfully.',
            'data': serializer.data
        })


class JoinRoomView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        # print(dir(request))
        request.data._mutable = True
        if not request.session.session_key:
            request.session.save()
        request.data['session'] = request.session.session_key
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Room created successfully.',
            'data': serializer.data
        })
