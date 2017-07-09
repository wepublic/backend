from rest_framework import permissions
from users import utils


'''Allow unauthenticated users to Create a user
forbid Users to see other users, except staff members
'''
class ReadOnlyAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False
    




