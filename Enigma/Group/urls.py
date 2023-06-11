from django.urls import path
from django.urls import path, re_path
from Group.views import GroupInfo, CreateGroup, DeleteGroup, AddUserGroup, ShowMembers, ShowGroups
#just simple comment
app_name = 'Group'

urlpatterns = [

    path('GroupInfo/', GroupInfo.as_view(), name='GroupInfo'),
    path('DeleteGroup/', DeleteGroup.as_view(), name='DeleteGroup'),
    path('ShowMembers/', ShowMembers.as_view(), name='ShowMembers'),
    path('ShowGroups/', ShowGroups.as_view(), name='ShowGroups'),
    path('CreateGroup/', CreateGroup.as_view(), name='CreateGroup'),
    path('AddUserGroup/', AddUserGroup.as_view(), name='AddUserGroup'),


]
