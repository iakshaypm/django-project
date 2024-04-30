from rest_framework import permissions


class CanCreateRoom(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 2:
            if request.data['type'] == 1:
                return True
        elif request.user.user_type == 3:
            if request.data['type'] == 2:
                return True
        elif request.user.user_type == 4:
            if request.data['type'] == 3:
                return True
        return False
