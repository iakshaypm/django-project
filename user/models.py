from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Permission
from classroom.models import Classroom
from assignment.models import Assignment


class MyAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            return ValueError("Users must have a email address.")
        if not extra_fields['phone_number']:
            return ValueError("Users must have a phone number.")

        user = self.model(
            email=self.normalize_email(email).lower(),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            **extra_fields
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Account(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOOSES = (
        (1, 'Student'),
        (2, 'Teacher'),
        (3, 'HOD'),
        (4, 'Management'),
        (5, 'Parent')
    )
    username = None
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    name = models.CharField(max_length=60)
    phone_number = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(verbose_name='last_login', auto_now=True, null=True)
    user_type = models.PositiveIntegerField(choices=USER_TYPE_CHOOSES, default=1)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']
    objects = MyAccountManager()


class Student(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, unique=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.DO_NOTHING, related_name='student_classroom')
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    date_of_birth = models.DateTimeField()
    parent = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='parents')
    assignment = models.ForeignKey(Assignment, null=True, on_delete=models.DO_NOTHING)


class Subject(models.Model):
    name = models.CharField(max_length=80)


class Teacher(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    classroom = models.OneToOneField(Classroom, on_delete=models.DO_NOTHING)


class HOD(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
