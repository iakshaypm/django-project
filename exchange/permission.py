from rest_framework import permissions


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
