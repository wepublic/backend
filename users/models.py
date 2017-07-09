from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from wepublic_backend import settings

from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, first_name="", last_name="", zip_code="", year_of_birth=None, gender="", password=None, profile_pic=""):
        if not email:
            raise ValueError('Email-Address needs to be set!')

        user = self.model(
                email = email,
                username=username,
                first_name=first_name, 
                last_name=last_name,
                zip_code = zip_code,
                year_of_birth = year_of_birth,
                gender = gender,
                profile_pic = profile_pic,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, username, password, first_name="", last_name="", zip_code="", year_of_birth=None, gender="", profile_pic=""):
        user = self.create_user(email, username, first_name, last_name, zip_code, year_of_birth, gender, password, profile_pic)
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user



class User(AbstractBaseUser, PermissionsMixin):
    """
    Our own extension of djangos standard :model:`auth.User` class
    """


    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        'email Address', 
        unique=True,
        error_messages={
            'unique': 'A User with that email address already exists'
        }        
    )
    username = models.CharField(
        'username',
        max_length=150,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
    )

    first_name = models.CharField(blank=True, max_length=50)
    last_name = models.CharField(blank=True, max_length=50)
    reputation = models.IntegerField(default=0, blank=True)
    profile_pic = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True)
    zip_code = models.CharField(max_length=5, blank=True)
    year_of_birth = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(blank=True, max_length = 30)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.username


    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
