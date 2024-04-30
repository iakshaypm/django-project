from rest_framework import views, status
from rest_framework import generics
from .serializers import QuestionSerializer, CommentSerializer, UpvoteSerializer
from .permission import IsStudent, CanAccessComment, CanUpvote, CanRemoveUpvote, CanAddComment, IsTeacher
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Question, Comment, Upvote


class QuestionCreateView(views.APIView):
    permission_classes = (IsAuthenticated, IsStudent,)

    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Question created successfully',
            'data': serializer.data
        })


class QuestionListView(generics.ListAPIView):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticated, IsStudent,)
    serializer_class = QuestionSerializer


class QuestionRetrieveView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticated, IsStudent, )
    serializer_class = QuestionSerializer


class QuestionUpdateView(generics.UpdateAPIView):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticated, IsStudent,)
    serializer_class = QuestionSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Question has been updated.',
            'data': serializer.data
        })


class QuestionDeleteView(generics.DestroyAPIView):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticated, IsStudent,)
    serializer_class = QuestionSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Question has been deleted.',
            'data': {}
        })


class CommentCreateView(views.APIView):
    permission_classes = (IsAuthenticated, IsTeacher, CanAddComment, )

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Comment added successfully',
            'data': serializer.data
        })


class CommentListView(generics.ListAPIView):
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated, IsStudent,)
    serializer_class = CommentSerializer


class CommentRetrieveView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated, CanAccessComment,)
    serializer_class = CommentSerializer


class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated, CanAccessComment,)
    serializer_class = CommentSerializer


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated, CanAccessComment,)
    serializer_class = CommentSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Comment has been deleted.',
            'data': {}
        })


class UpvoteCreateView(views.APIView):
    permission_classes = (IsAuthenticated, CanUpvote,)

    def post(self, request):
        serializer = UpvoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.check_object_permissions(request, Comment.objects.get(pk=request.data['comment']))
        serializer.save(user=request.user)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Upvote added successfully',
            'data': serializer.data
        })


class UpvoteDeleteView(generics.DestroyAPIView):
    queryset = Upvote.objects.all()
    permission_classes = (IsAuthenticated, CanRemoveUpvote,)
    serializer_class = UpvoteSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Upvote has been removed.',
            'data': {}
        })
