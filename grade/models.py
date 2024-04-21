from django.db import models
from user.models import Account


class Mark(models.Model):
    student = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='student_id')
    teacher = models.ForeignKey(Account, on_delete=models.CASCADE)
    sub1 = models.CharField(max_length=20)
    sub2 = models.CharField(max_length=20)
    sub3 = models.CharField(max_length=20)

