from django.db import models
from user.models import Account


# Create your models here.

class MainAttendance(models.Model):
    ATTENDANCE_TYPE_CHOOSES = (
        (1, 'Student'),
        (2, 'Teacher'),
        (3, 'HOD'),
    )
    attendance_type = models.PositiveIntegerField(choices=ATTENDANCE_TYPE_CHOOSES)
    date_of_producing = models.DateField(auto_now=True)
    initiated_by = models.ForeignKey(Account, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ('attendance_type', 'date_of_producing',)
        db_table = "attendance_main"


class StudentAttendance(models.Model):
    attendance = models.OneToOneField(MainAttendance, on_delete=models.DO_NOTHING)
    student = models.ForeignKey(Account, on_delete=models.CASCADE)
    date_of_marking = models.DateField(auto_now=True)

    class Meta:
        db_table = "attendance_student"


class TeacherAttendance(models.Model):
    attendance = models.OneToOneField(MainAttendance, on_delete=models.DO_NOTHING)
    teacher = models.ForeignKey(Account, on_delete=models.CASCADE)
    date_of_marking = models.DateField(auto_now=True)

    class Meta:
        db_table = "attendance_teacher"


class HodAttendance(models.Model):
    attendance = models.OneToOneField(MainAttendance, on_delete=models.DO_NOTHING)
    hod = models.ForeignKey(Account, on_delete=models.CASCADE)
    date_of_marking = models.DateField(auto_now=True)

    class Meta:
        db_table = "attendance_hod"
