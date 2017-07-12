from rest_framework import permissions


class UserViewPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        print(obj.pk)
        if request.method == "POST":
            return True
        if request.user.groups.filter(name="staff").exists():
            return True
        else:
            return request.user.pk == obj.pk
