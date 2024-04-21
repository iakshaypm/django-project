from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 1:
            return request.user
        return False

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.user_type == 2:
            return True
        return False


class CanAccessComment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanUpvote(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user != request.user


class CanRemoveUpvote(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
