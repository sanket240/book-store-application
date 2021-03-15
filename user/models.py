from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if username is None:
            raise TypeError('User should have a username')

        if email is None:
            raise TypeError('User should have a Email')
        user = self.model(
            username=username,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        if password is None:
            raise TypeError('Password can not be none')

        user = self.create_user(email, username, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.is_verified = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=200, unique=True, db_index=True)
    email = models.CharField(max_length=200, unique=True, db_index=True)  # make sure it gets an valid email field
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone = models.BigIntegerField()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def get_email(self):
        return self.email

    def __str__(self):
        return self.email


class UserOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_st = models.DateTimeField(auto_now=True)
    otp = models.BigIntegerField()
