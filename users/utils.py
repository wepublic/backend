from django.utils.crypto import get_random_string
import hashlib

from django.template.loader import render_to_string
from django.conf import settings
import requests

from wepublic_backend.settings import SUPPORT_ADDRESS, NOREPLY_ADDRESS

from post_office import mail


def is_staff_user(user):
    return user.groups.filter(name="staff").exists()


def is_politician_user(user):
    return user.groups.filter(name="politician").exists()


def generate_random_key(username):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(20, chars)
    return hashlib.sha256((secret_key+username).encode('utf-8')).hexdigest()


def send_mail(re, plain, sender, recipients, html_message):

    mail.send(
        recipients=recipients,
        sender=sender,
        template=None,
        context=None,
        subject=re,
        message=plain,
        html_message=html_message,
        priority="high"
    )


def send_activation_mail(username, activation_link, recipient):
    params = {'username': username, 'link': activation_link, 'support': SUPPORT_ADDRESS}
    plain = render_to_string('users/mails/activation_email.txt', params)
    html = render_to_string('users/mails/activation_email.html', params)
    send_mail(
            'Dein Konto bei +me',
            plain,
            NOREPLY_ADDRESS,
            [recipient],
            html_message=html
    )


def send_password_reset_mail(username, password_reset_link, recipient):
    params = {'username': username, 'link': password_reset_link, 'support': SUPPORT_ADDRESS}
    plain = render_to_string('users/mails/password_reset_email.txt', params)
    html = render_to_string('users/mails/password_reset_email.html', params)
    send_mail(
            'Dein Passwort bei +me zurücksetzen',
            plain,
            NOREPLY_ADDRESS,
            [recipient],
            html_message=html
    )


def slack_notify_question(question, link):
    if not settings.SLACK_NOTIFICATIONS_ACTIVE:
        return
    json = {
            "text": "Die Folgende Frage hat grade am meisten Upvotes: ",
            "channel": "#produktentwicklung",
            "attachments": [
                {
                    "fallback": "\"{}\": <{}|Link>".format(
                        question,
                        link),
                    "pretext": "\"{}\": <{}|Link>".format(
                        question,
                        link),
                    "color": "#D00000",
                    "fields": [
                        {
                            "title": "Frage",
                            "value": question.text,
                            "short": False
                        }
                    ]
                }
            ]
        }
    requests.post(settings.SLACK_NOTIFICATIONS_URL, json=json)

def slack_notify_report(question, reason, link, reporter):
    if not settings.SLACK_NOTIFICATIONS_ACTIVE:
        return
    json = {
            "text": "Eine Frage wurde von {} gemeldet:".format(
                reporter.email),
            "attachments": [
                {
                    "fallback": "\"{}\": <{}|Link>".format(
                        question,
                        link),
                    "pretext": "\"{}\": <{}|Link>".format(
                        question,
                        link),
                    "color": "#D00000",
                    "fields": [
                        {
                            "title": "Begründung",
                            "value": reason,
                            "short": False
                        }
                    ]
                }
            ]
        }
    requests.post(settings.SLACK_NOTIFICATIONS_URL, json=json)
