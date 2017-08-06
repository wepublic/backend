
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.conf import settings
from users.models import ReputationAction


class Command(BaseCommand):
    help = 'Adds the default repuation values from settings.py to db'

    def handle(self, *args, **options):

        for rep_value in settings.WP_DEFAULT_REPUTATION:
            obj, created = ReputationAction.objects.get_or_create(
                    action=rep_value['action'],
                    defaults={
                        'value': rep_value['value'],
                    },
                )
            print("Action {} created: {}".format(obj, created))
