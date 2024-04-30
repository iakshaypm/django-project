from django.db import models


# Create your models here.

class Classroom(models.Model):
    name = models.CharField(max_length=20, unique=True)
    total_strength = models.IntegerField()
