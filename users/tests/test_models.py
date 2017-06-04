from django.test import TestCase
from django.contrib.auth import User

from users.model import UserProfile


class UserTest(TestCase):
    
    def setUp(self):
