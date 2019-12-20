import logging
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


logger = logging.getLogger('eLearning')


def _is_valid_credentials(func):
        def wrapper(self, email, first_name, last_name, password):
            if not email:
                logger.warning("Attempt to create a user without email.")
                raise ValueError("User must have an email address.")
            if not first_name:
                logger.warning("Attempt to create a user without first name.")
                raise ValueError("User must have a first name.")
            if not last_name:
                logger.warning("Attempt to create a user without last name.")
                raise ValueError("User must have a last name.")
            if not password:
                logger.warning("Attempt to create a user without password.")
                raise ValueError("User must have a password.")
            func(self, email, first_name, last_name, password)
        return wrapper


# TODO: fix transfering user from create user to create_superuser
class AccountManager(BaseUserManager):
    @_is_valid_credentials
    def create_user(self, email, first_name, last_name, password):
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        # print(f'create user: {user}')
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user = Account.objects.get(email=email)
        # print(f'create superuser: {user}')
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    favorite_courses = models.ManyToManyField('courses.Course') 
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = AccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
