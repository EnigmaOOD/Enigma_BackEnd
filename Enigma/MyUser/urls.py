from django.urls import path, re_path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterUsers, UserInfo, EditProfile
urlpatterns = [
    path('token/', obtain_auth_token),
    path('register/', RegisterUsers.as_view()),
    path('UserInfo/', UserInfo.as_view()),
    path('EditProfile/', EditProfile.as_view(), name="EditProfile"),
]