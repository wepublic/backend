from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.authtoken.models import Token
from users.models import User
from django.contrib.auth import authenticate

import pprint


class UserTest(APITestCase):
    normal_user=None
    super_user=None
    pp = pprint.PrettyPrinter(indent=4)

    def setUp(self):
        # create two users, one normal, one superuser
        self.normal_user = User.objects.create_user(
                username='normal',
                password='password',
                email='normal@example.com',
                first_name='Ralf',
                last_name='Freu',
                zip_code=13,
                year_of_birth=1989)
        self.super_user = User.objects.create_user(
                username='super',
                password='password',
                email='super@example.com',
                first_name='Hans',
                last_name='Frei')
        self.normal_user.is_active = True
        self.normal_user.save()
        self.super_user.is_active = True
        self.super_user.save()

    def test_get_and_create_token(self):
        if Token.objects.filter(user=self.normal_user).count() > 0 :
            Token.objects.get(user=self.normal_user).delete()
        data = {'email': 'normal@example.com', 'password': 'password' }
        response = self.client.post('/Users/token/', data)
        normal_user_token = Token.objects.get(user=self.normal_user)
        self.assertEqual(normal_user_token.key, response.data['Token'])

    def test_get_existing_token(self):
        if Token.objects.filter(user=self.normal_user).count() == 0 :
            Token.objects.create(user=self.normal_user)
        data = { 'email': self.normal_user.email, 'password': 'password' }
        response = self.client.post('/Users/token/', data)
        self.assertEqual(Token.objects.get(user=self.normal_user).key, response.data['Token'])

    def test_get_token_no_email_or_password(self):
        data = { 'email': self.normal_user.email }


    

        


