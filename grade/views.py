from rest_framework import views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics

from .serializer import MarkSerializer
from .permission import IsTeacher, IsStudent
from .models import Mark


class MarkCreateView(views.APIView):
    permission_classes = (IsAuthenticated, IsTeacher)

    def post(self, request):
        serializer = MarkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(teacher=request.user)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Mark has been added',
            'data': serializer.data
        })


class MarkListView(generics.ListAPIView):
    queryset = Mark.objects.all()
    permission_classes = (IsAuthenticated, IsTeacher, )
    serializer_class = MarkSerializer


class MarkDeleteView(generics.DestroyAPIView):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
    permission_classes = (IsAuthenticated, IsTeacher, )


