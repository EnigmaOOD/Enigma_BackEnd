from django.urls import path
from . import views
from django.urls import path, re_path
from .views import CreateGroup, DeleteGroup, AddUserGroup, AmountofDebtandCredit

app_name = 'Group'
urlpatterns = [

    path('GroupInfo/', views.GroupInfo.as_view(), name='GroupInfo'),
    path('DeleteGroup/', views.DeleteGroup.as_view(), name='DeleteGroup'),
    path('ShowMembers/', views.ShowMembers.as_view(), name='ShowMembers'),
    path('ShowGroups/', views.ShowGroups.as_view(), name='ShowGroups'),
    path('CreateGroup/', CreateGroup.as_view(), name='CreateGroup'),
    path('AddUserGroup/', AddUserGroup.as_view(), name='AddUserGroup'),
    path('AmountofDebtandCredit/', AmountofDebtandCredit.as_view(), name='AmountofDebtandCredit'),


]
