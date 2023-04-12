from django.urls import path, re_path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterUsers, VerifyEmail

urlpatterns = [
    path('token/', obtain_auth_token, name="token"),
    path('register/', RegisterUsers.as_view(), name="register"),
    path('verify-email/', VerifyEmail.as_view(), name="verify-email"),

]