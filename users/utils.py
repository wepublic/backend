def is_staff_user(user):
    return user.groups.filter(name="staff").exists()


def is_politician_user(user):
    return user.groups.filter(name="politician").exists()
