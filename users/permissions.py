from rest_framework import permissions




class IsAllowedToViewAndChangeUsers(permissions.BasePermission):

    def has_object_permission( self, request, view, obj):
        if request.user.groups.filter(name="staff").exists():
            return true
        else: 
            return request.user == obj.user
