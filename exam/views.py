from rest_framework import views, status
from rest_framework.response import Response

from user.permission import IsTeacher, IsStudent
from rest_framework.permissions import IsAuthenticated
from .serializers import ExamSerializer

from user.models import Teacher, Student
from classroom.models import Classroom

from twilio.rest import Client
from django.conf import settings


class ExamCreateView(views.APIView):
    permission_classes = (IsAuthenticated, IsTeacher,)

    def post(self, request):
        serializer = ExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        teacher = Teacher.objects.filter(user_id=request.user).get()
        parents_phoneno = Student.objects.filter(classroom_id=teacher.classroom_id).values_list('parent__phone_number',
                                                                                                flat=True)
        serializer.save(classroom=Classroom.objects.get(id=teacher.classroom_id))
        self.send_sms(list(parents_phoneno))
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Exam created successfully',
            'data': serializer.data
        })

    def send_sms(self, phone_number):
        response = []
        message = 'Exam has scheduled'
        from_ = '+14192739589'
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        for to in phone_number:
            response = client.messages.create(body=message, to=to, from_=from_)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Message has been send.',
            'data': response
        })
