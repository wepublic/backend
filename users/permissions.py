from rest_framework import permissions
from pprint import PrettyPrinter


'''
This Allows unauthenticated users to create a user, but lets them only view
and change themselves afterwards. 
Staff Users can do everything
'''
class UserViewPermission(permissions.BasePermission):
    
#    def has_permission (self, request, view):
#        PrettyPrinter(indent=4, depth=3).pprint(request.__dict__)
#        if request.method == "POST":
#            return True
#        if request.user.groups.filter(name="staff").exists():
#            return True

    def has_object_permission( self, request, view, obj):
        print(obj.pk)
        if request.method == "POST":
            return True
        if request.user.groups.filter(name="staff").exists():
            return True
        else: 
            return request.user.pk == obj.pk
