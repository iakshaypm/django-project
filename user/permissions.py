from rest_framework import permissions


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 2:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return False
