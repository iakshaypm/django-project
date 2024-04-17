from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Permission


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

        # p_add = Permission.objects.get(codename='add_account')
        # p_change = Permission.objects.get(codename='change_account')
        # if extra_fields['user_type'] > 1:
        #     user.user_permissions.set([p_add, p_change])

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
    # class Meta:
    #     permissions = (
    #         ('add_student', 'Add Students'),
    #     )

    USER_TYPE_CHOOSES = (
        (1, 'Student'),
        (2, 'Teacher'),
        (3, 'HOD'),
        (4, 'Management')
    )
    username = None
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    name = models.CharField(max_length=60)
    phone_number = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(verbose_name='last_login', auto_now=True, null=True)
    user_type = models.PositiveIntegerField(choices=USER_TYPE_CHOOSES, default=1)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']
    objects = MyAccountManager()


class Student(models.Model):
    user_id = models.OneToOneField(Account, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    date_of_birth = models.DateTimeField()


class Teacher(models.Model):
    class Meta:
        permissions = (
            ('add_student', 'Add Students'),
        )

    user_id = models.OneToOneField(Account, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)


class HOD(models.Model):
    class Meta:
        permissions = (
            ('add_student', 'Add Students'),
            ('add_teacher', 'Add Teacher'),
        )

    user_id = models.OneToOneField(Account, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
