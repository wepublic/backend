from django.db import models
from django.utils import timezone
import datetime
# from django.urls import reverse
from rest_framework.reverse import reverse_lazy
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework.authtoken.models import Token
from users.utils import generate_random_key
from users.utils import send_activation_mail
from users.utils import send_password_reset_mail


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username="", first_name="", last_name="",
                    zip_code="", year_of_birth=None, gender="",
                    password=None, profile_pic=""):
        if not email:
            raise ValueError('Email-Address needs to be set!')

        user = self.model(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                zip_code=zip_code,
                year_of_birth=year_of_birth,
                gender=gender,
                profile_pic=profile_pic,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, first_name="",
                         last_name="", zip_code="", year_of_birth=None,
                         gender="", profile_pic=""):
        user = self.create_user(email, username, first_name, last_name,
                                zip_code, year_of_birth, gender,
                                password, profile_pic)
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


class ReputationAction(models.Model):
    action = models.CharField(max_length=50, unique=True)
    value = models.IntegerField()

    def __str__(self):
        return "{}: {}".format(self.action, self.value)


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
        help_text='150 characters. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        blank=True,
    )

    first_name = models.CharField(blank=True, max_length=50)
    last_name = models.CharField(blank=True, max_length=50)
    reputation = models.IntegerField(default=0, blank=True)
    profile_pic = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True)
    zip_code = models.CharField(max_length=5, blank=True)
    year_of_birth = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(blank=True, max_length=30)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    activation_key = models.CharField(max_length=80, blank=True)
    activation_key_exprires = models.DateTimeField(null=True, blank=True)
    reset_password_key = models.CharField(max_length=80, blank=True)
    reset_password_key_expires = models.DateTimeField(null=True, blank=True)
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

    def get_token(self):
        return Token.objects.get_or_create(user=self)[0]

    def remove_token(self):
        try:
            Token.objects.get(user=self).delete()
        except Token.DoesNotExist:
            print('token does not exists')
            pass

    def new_activation_link(self):
        exp = timezone.now() + datetime.timedelta(days=1)

        self.activation_key = generate_random_key(self.email)
        self.activation_key_exprires = exp
        self.save()

    def new_password_reset_link(self):
        exp = timezone.now() + datetime.timedelta(days=1)

        self.reset_password_key = generate_random_key(self.email)
        self.reset_password_key_expires = exp
        self.save()

    def send_validation_link(self, request):

        if self.activation_key is None or self.activation_key == '':
            self.new_activation_link()
        if (self.activation_key_exprires is not None
                and timezone.now() > self.activation_key_exprires):
            self.new_activation_link()

        path = reverse_lazy('user-activate', request=request)
        link = "{}?key={}".format(path, self.activation_key)
        if self.username is not '':
            name = self.username
        else:
            name = self.email
        send_activation_mail(name, link, self.email)

    def password_reset_link(self, request):

        if self.reset_password_key is None or self.reset_password_key == '':
            self.new_password_reset_link()
        if (self.reset_password_key_expires is not None
                and timezone.now() > self.reset_password_key_expires):
            self.new_password_reset_link()

        path = reverse_lazy('user-reset-password-page',
                            request=request
                            )
        link = "{}?key={}".format(path, self.reset_password_key)
        if self.username is not '':
            name = self.username
        else:
            name = self.email
        send_password_reset_mail(name, link, self.email)

    def update_reputation(self, action):
        value = ReputationAction.objects.get(action=action).value
        print(self.reputation)
        if value + self.reputation < 0:
            return False
        else:
            self.reputation += value
            self.save()
            return True
