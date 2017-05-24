from django.contrib.auth.models import User

def is_staff_user(user):
    return user.groups.filter(name="staff").exists()
