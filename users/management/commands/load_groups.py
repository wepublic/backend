
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, User
class Command(BaseCommand):
    help = 'Add the groups \'staff\' and \'politician\' to the Database and add all Superusers to staff'


    def handle(self, *args, **options):
        staff_group = Group.objects.get_or_create(name="staff")[0]
        politician_group = Group.objects.get_or_create(name="politician")[0]

        admins = User.objects.filter(is_superuser=True)

        for u in admins:
            staff_group.user_set.add(u)

        staff_group.save()
