from django.db import models


class Assignment(models.Model):
    ASSIGNMENT_TYPE_CHOOSES = (
        (1, 'A'),
        (2, 'B'),
        (3, 'C'),
        (4, 'D'),
        (5, 'E')
    )
    name = models.CharField(max_length=50)
    type = models.IntegerField(choices=ASSIGNMENT_TYPE_CHOOSES)

    class Meta:
        db_table = 'assignment'


class AssignmentMark(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    mark = models.CharField(max_length=50)

    class Meta:
        db_table = 'assignment_mark'
