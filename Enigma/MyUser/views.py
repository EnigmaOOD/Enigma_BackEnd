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

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status


class RegisterUser(generics.GenericAPIView):

    serializer_class = MyUserSerializer

    def post(self, request):
        user = request.data 
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = MyUser.objects.get(email=user_data['email'])

        token, created = Token.objects.get_or_create(user=user)


        current_site = get_current_site(request).domain
        relativeLink=reverse('verify-email')
        
        absurl = 'http://' + current_site + relativeLink+"?token="+str(token)
        email_body ='Hi '+user.username+' Use link below to verify your email \n'+absurl
        data = {'email_body':email_body, 'email_subject':'Verify your email', 'to_email':[user.email]}
        print(data)
        print("---------------------------------------------------------------------")
        Util.send_email(data)
        print("---------------------------------------------------------------------")
        return Response(user_data, status=status.HTTP_201_CREATED)  

class VerifyEmail(generics.GenericAPIView):

    def get(self, request):
        token = request.query_params.get('token')
        if token:
            try:
                user = Token.objects.get(key=token).user
                user.is_active = True
                user.save()
                return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
            except Token.DoesNotExist:
                return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Token parameter is missing.'}, status=status.HTTP_400_BAD_REQUEST)