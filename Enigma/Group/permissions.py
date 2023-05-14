from rest_framework.permissions import BasePermission
from MyUser.models import MyUser
from .models import Group, Members
from rest_framework.exceptions import PermissionDenied



class IsGroupUser(BasePermission):
    def has_permission(self, request, view):
        is_group_member = False
        try:
            members = Members.objects.filter(userID=request.user, groupID=request.data['groupID'])
            if members:
                is_group_member = True 
            return request.user and request.user.is_authenticated and is_group_member
        except:
            pass
        raise PermissionDenied('You do not have permission to perform this action.')



