from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ClassroomSerializer
from .permission import IsManagement, IsTeacher
from .models import Classroom


class ClassroomCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsManagement)

    def post(self, request, *args, **kwargs):
        serializer = ClassroomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Classroom attendance successfully.',
            'data': serializer.data
        })


class ClassroomListView(generics.ListAPIView):
    queryset = Classroom.objects.all()
    permission_classes = (IsAuthenticated, IsTeacher,)
    serializer_class = ClassroomSerializer
