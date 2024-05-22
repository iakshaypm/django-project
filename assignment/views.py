from django.core.mail import send_mail, send_mass_mail

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import AssignmentSerializer, AssignmentMarkSerializer


class AssignmentCreate(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = AssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Assignment has been created.',
            'data': serializer.data
        })


class AssignmentMarkCreate(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = AssignmentMarkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Mark for the assignment has been added.',
            'data': serializer.data
        })


def simple_mail(request):
    message1 = ('Subject here', 'Here is the message', 'from@example.com', ['ambadiakshay25@gmail.com', 'akshay'
                                                                                                        '.prabhakaran'
                                                                                                        '@qburst.com'])
    message2 = ('Another Subject', 'Here is another message', 'from@example.com', ['abhinandndev@gmail.com'])
    send_mass_mail((message1, message2), fail_silently=False)
    return Response({
        'status': status.HTTP_200_OK,
        'message': 'Email has send successfully',
        'data': []
    })
