from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from users.models import User

import pprint


class UserTest(APITestCase):
    normal_user = None
    super_user = None
    pp = pprint.PrettyPrinter(indent=4)
    create_user = {
            "username": "new_man",
            "email": "new@example.com",
            "password": "test1234",
            "first_name": "Neuer",
            "last_name": "User",
            "zip_code": "423",
            "year_of_birth": 1967,
            "gender": "M"
            }

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
        if Token.objects.filter(user=self.normal_user).count() > 0:
            Token.objects.get(user=self.normal_user).delete()
        data = {'email': 'normal@example.com', 'password': 'password'}
        response = self.client.post('/Users/token/', data)
        normal_user_token = Token.objects.get(user=self.normal_user)
        self.assertEqual(normal_user_token.key, response.data['Token'])

    def test_get_existing_token(self):
        if Token.objects.filter(user=self.normal_user).count() == 0:
            Token.objects.create(user=self.normal_user)
        data = {'email': self.normal_user.email, 'password': 'password'}
        response = self.client.post('/Users/token/', data)
        self.assertEqual(Token.objects.get(user=self.normal_user).key,
                         response.data['Token'])

    def test_logout(self):
        if Token.objects.filter(user=self.normal_user).count() == 0:
            Token.objects.create(user=self.normal_user)
        token = Token.objects.get(user=self.normal_user)
        token_string = 'Token {}'.format(token.key)
        self.client.get('/Users/logout/', HTTP_AUTHORIZATION=token_string)
        self.assertEqual(
                Token.objects.filter(user=self.normal_user).count(),
                0
            )

    def test_get_token_no_email_or_password(self):
        data_no_pw = {'email': self.normal_user.email}
        data_no_em = {'password': 'password'}

        res = self.client.post('/Users/token/', data_no_pw)
        self.assertEqual(res.status_code, 400)
        res = self.client.post('/Users/token/', data_no_em)
        self.assertEqual(res.status_code, 400)

    def test_get_token_wrong_password_or_email(self):
        data_wrong_pw = {'email': self.normal_user.email,
                         'password': 'blabla'}
        data_wrong_em = {'email': 'emailwmdjs@examp',
                         'password': 'password'}
        res = self.client.post('/Users/token/', data_wrong_pw)
        self.assertEqual(res.status_code, 403)
        res = self.client.post('/Users/token/', data_wrong_em)
        self.assertEqual(res.status_code, 403)

    def test_get_me(self):
        res = self.client.get(
                '/Users/me/',
                HTTP_AUTHORIZATION=self.get_token_string(self.normal_user)
            )
        self.assertEqual(self.normal_user.pk, res.data['id'])

    def test_add_valid_complete_user(self):
        user = dict(self.create_user)
        self.user_creation_valid_with_dict_test(user)

    def test_add_valid_small_user(self):
        user = dict(self.create_user)
        del user['first_name']
        del user['last_name']
        del user['zip_code']
        del user['gender']
        del user['year_of_birth']
        self.user_creation_valid_with_dict_test(user)

    def test_add_user_no_mail(self):
        user = dict(self.create_user)
        del user['email']
        res = self.client.post('/Users/', user)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data['email'], ['This field is required.'])

    def test_add_user_no_pw(self):
        user = dict(self.create_user)
        del user['password']
        res = self.client.post('/Users/', user)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data['password'], ['This field is required.'])

    def test_add_user_no_username(self):
        user = dict(self.create_user)
        del user['username']
        res = self.client.post('/Users/', user)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data['username'], ['This field is required.'])

    def test_add_user_invalid_password(self):
        user = dict(self.create_user)
        user['password'] = 'test'
        res = self.client.post('/Users/', user)
        self.assertEqual(res.status_code, 400)

    def test_add_user_invalid_mail(self):
        user = dict(self.create_user)
        user['email'] = 'test'
        res = self.client.post('/Users/', user)
        self.assertEqual(res.status_code, 400)

    def test_change_username(self):
        token_string = self.get_token_string(self.normal_user)
        username_dict = {'username': 'changed'}
        self.client.patch(
                '/Users/{}/'.format(self.normal_user.pk),
                username_dict, HTTP_AUTHORIZATION=token_string)
        alteredUser = User.objects.get(pk=self.normal_user.pk)
        self.assertEqual(alteredUser.username, 'changed')

    def test_change_first_name(self):
        token_string = self.get_token_string(self.normal_user)
        first_name_dict = {'first_name': 'new_name'}
        self.client.patch(
                '/Users/{}/'.format(self.normal_user.pk),
                first_name_dict, HTTP_AUTHORIZATION=token_string)
        alteredUser = User.objects.get(pk=self.normal_user.pk)
        self.assertEqual(alteredUser.first_name, 'new_name')

    def get_token_string(self, user):
        return "Token {}".format(user.get_token().key)

    def assertEqualThree(self, one, two, three):
        self.assertEqual(one, two)
        self.assertEqual(two, three)

    def user_creation_valid_with_dict_test(self, user_dict):
        res = self.client.post('/Users/', user_dict)
        self.assertEqual(res.status_code, 201)
        new_user = User.objects.get(email=user_dict['email'])
        self.assertEqual(new_user.get_token().key, res.data['token'])

        for key, value in user_dict.items():
            if key != 'password':
                self.assertEqualThree(
                        new_user.__dict__[key],
                        res.data[key],
                        value
                    )
        self.assertEqual(new_user.is_staff, False)
