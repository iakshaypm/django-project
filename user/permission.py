from rest_framework import permissions


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 2:
            return True
        return False


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 1:
            return True
        return False


class IsHOD(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 3:
            return True
        return False


class IsManagement(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 4:
            return True
        return False
