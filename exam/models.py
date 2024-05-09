from django.db import models

from classroom.models import Classroom


# Create your models here.
class Exam(models.Model):
    name = models.CharField(max_length=20, unique=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    class Meta:
        db_table = 'exam'
