
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.db.utils import IntegrityError

from users.models import User
from wepublic_backend.settings import WP_DEFAULT_STAFF_USER, WP_DEFAULT_STAFF_USER_EMAIL


class Command(BaseCommand):
    help = 'Add the groups \'staff\' and \'politician\' to the Database and add all Superusers to staff'

    def handle(self, *args, **options):
        staff_group = Group.objects.get_or_create(name="staff")[0]
        Group.objects.get_or_create(name="politician")[0]

        try:
            user = User.objects.create_user(WP_DEFAULT_STAFF_USER_EMAIL, WP_DEFAULT_STAFF_USER, User.objects.make_random_password())
            user.is_staff = True
            user.save()
            print("Staff user created")
        except IntegrityError:
            print("Staff user exists")
            user = User.objects.get(email=WP_DEFAULT_STAFF_USER_EMAIL)

        from pprint import pformat
        print("Staff (backup) user:", pformat(user))

        admins = User.objects.filter(is_admin=True)

        for u in admins:
            print(u.username)
            staff_group.user_set.add(u)

        staff_group.save()
