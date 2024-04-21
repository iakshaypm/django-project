from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Permission
from user.models import Account, Subject


class Question(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    tag = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)


class Comment(models.Model):
    content = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)


class Upvote(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('comment', 'user',)

