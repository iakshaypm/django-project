from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


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
        (1, 'student'),
        (2, 'teacher'),
        (3, 'secretary'),
        (4, 'supervisor'),
    )
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
