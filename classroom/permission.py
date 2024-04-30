from rest_framework import permissions


class IsManagement(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 4:
            return True
        return False


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 2:
            return True
        return False
