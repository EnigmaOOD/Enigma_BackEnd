from django.urls import path, re_path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterUser, VerifyEmail, UserInfo, EditProfile, LeaveGroup

urlpatterns = [
    path('token/', obtain_auth_token, name="token"),
    path('register/', RegisterUser.as_view(), name="register"),
    path('verify-email/', VerifyEmail.as_view(), name="verify-email"),
    path('UserInfo/', UserInfo.as_view(), name="UserInfo"),
    path('EditProfile/', EditProfile.as_view(), name="EditProfile"),
    path('LeaveGroup/', LeaveGroup.as_view(), name="LeaveGroup")
]