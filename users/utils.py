from django.utils.crypto import get_random_string
import hashlib

from django.core.mail import send_mail
from django.template.loader import render_to_string


def is_staff_user(user):
    return user.groups.filter(name="staff").exists()


def is_politician_user(user):
    return user.groups.filter(name="politician").exists()


def generate_activation_key(username):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(20, chars)
    return hashlib.sha256((secret_key+username).encode('utf-8')).hexdigest()


def send_activation_mail(username, activation_link, recipient):
    params = {'username': username, 'link': activation_link}
    plain = render_to_string('users/activation_email.txt', params)
    html = render_to_string('users/activation_email.html', params)
    send_mail(
            'Dein Konto bei +me',
            plain,
            'admin@wepublic.me',
            [recipient],
            html_message=html
    )
