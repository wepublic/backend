from django.db import models
from django.contrib.auth.models import User
from wepublic_backend import settings

# Create your models here.

class Userprofile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    reputation = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True)

    
