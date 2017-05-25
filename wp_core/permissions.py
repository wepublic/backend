from rest_framework import permissions
from users import utils


'''Allow unauthenticated users to Create a user
forbid Users to see other users, except staff members
'''
class IsStaffOrTargetUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # allow user to list all users if logged in user is staff
        return view.action == 'retrieve' or request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        # allow logged in user to view own details, allows staff to view all records
        return request.user.is_staff or obj == request.user


# Everyone can see, only staff can modify
class OnlyStaffCanModify(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return utils.is_staff_user(request.user)

class StaffOrOwnerCanModify():
    def has_permission(self, request, view):
        #return request.method in permissions.SAFE_METHODS or request.method == 'POST'
        return True

    def has_object_permission(self, request, view, obj):
        print(request.__dict__)
        return request.method in permissions.SAFE_METHODS or utils.is_staff_user(request.user) or obj.creator == request.user
