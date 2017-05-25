from django.db import models
from django.contrib.auth.models import User
from wepublic_backend import settings

from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Userprofile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    reputation = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Userprofile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
