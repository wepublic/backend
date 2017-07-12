
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from users.models import User


class Command(BaseCommand):
    help = 'Add the groups \'staff\' and \'politician\' to the Database and add all Superusers to staff'

    def handle(self, *args, **options):
        staff_group = Group.objects.get_or_create(name="staff")[0]
        Group.objects.get_or_create(name="politician")[0]

        admins = User.objects.filter(is_admin=True)

        for u in admins:
            print(u.username)
            staff_group.user_set.add(u)

        staff_group.save()
