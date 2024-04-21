from rest_framework import permissions

from .models import MainAttendance


class CanAddAttendance(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.data['attendance_type'] == 1:
            if request.user.user_type == 2:
                return True
        elif request.data['attendance_type'] == 2:
            if request.user.user_type == 3:
                return True
        elif (request.data['attendance_type'] == 3 or request.data['attendance_type'] == 2
              or request.data['attendance_type'] == 1):
            if request.user.user_type == 4:
                return True
        else:
            return False


class CanMarkAttendance(permissions.BasePermission):
    def has_permission(self, request, view):

        attendance_id = request.data['attendance']
        attendance = MainAttendance.objects.get(id=attendance_id)
        if attendance.attendance_type == 1:
            if request.user.user_type == 1:
                return True
        elif attendance.attendance_type == 2:
            if request.user.user_type == 2:
                return True
        elif attendance.attendance_type == 3:
            if request.user.user_type == 3:
                return True
        else:
            return False


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 1:
            return request.user
        return False


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.user_type == 2:
            return True
        return False
