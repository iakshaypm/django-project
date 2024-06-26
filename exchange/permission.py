from rest_framework import permissions

from user.models import Teacher
from .models import Question


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 1:
            return request.user
        return False

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanAccessComment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanAddComment(permissions.BasePermission):
    def has_permission(self, request, view):
        teacher = Teacher.objects.get(user_id=request.user)
        question = Question.objects.get(id=request.data['question'])
        if teacher.subject.id == question.tag.id:
            return True
        return False


class CanUpvote(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user != request.user


class CanRemoveUpvote(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 2:
            return request.user
        return False
