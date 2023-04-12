from django.shortcuts import render
from .models import MyUser
from .serializers import MyUserSerializer
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework import generics
from rest_framework.generics import CreateAPIView
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse



"""class RegisterUsers(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = MyUserSerializer
"""
class RegisterUser(generics.GenericAPIView):

    serializer_class = MyUserSerializer

    def post(self, request):
        user = request.data 
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save
        user_data = serializer.validated_data['user']
        user = MyUser.objects.get(email=user_data['email'])

        token, created = Token.objects.get_or_create(user=user).key


        current_site = get_current_site(request).domain
        relativeLink=reverse('verify-email')
        
        absurl = 'http://' + current_site + relativeLink+"?token="+token
        Util.send_email(data)
        email_body ='Hi'+user.username+'Use link below to verify your email \n'+absurl
        data = {'email_body':email_body, 'email_subject':'Verify your email'}


        return Response({'token': token.key}) 

class VerifyEmail(generics.GenericAPIView):

    def get(self):
        pass