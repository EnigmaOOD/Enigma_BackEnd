from django.shortcuts import render
from .models import MyUser
from Group.models import Group, Members
from buy.models import buyer, consumer
from .serializers import MyUserSerializer, UpdateUserSerializer
from rest_framework import permissions, generics
from rest_framework.exceptions import ValidationError
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.generics import UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status




class RegisterUser(generics.GenericAPIView):

    permission_classes = [permissions.AllowAny]

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
        email_body ='Hi '+user.name+' Use link below to verify your email \n'+absurl
        data = {'email_body':email_body, 'email_subject':'Verify your email', 'to_email':[user.email]}
        print(data)
        print("---------------------------------------------------------------------")
        Util.send_email(data)
        print("---------------------------------------------------------------------")
        return Response(user_data, status=status.HTTP_201_CREATED)  

class VerifyEmail(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

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




"""
class ChangePasswordView(generics.UpdateAPIView):

    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
"""

class EditProfile(UpdateAPIView):
    
    users = MyUser.objects.all()
    serializer_class = UpdateUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    

class UserInfo(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        try:
            
            user = self.request.user
            if not MyUser.objects.filter(pk=user.pk).exists():
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
                
            user_info = {
                'user_id': user.user_id,
                'email': user.email,
                'name': user.name,
                'picture_id': user.picture_id,
                'is_active': user.is_active,
                'is_admin': user.is_admin,
                'is_staff': user.is_staff,
            }

            return Response({'user_info': user_info})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteUser(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.data['userID']
            group_id = request.data['groupID']
            if DebtandCreditforMemberinGroup(user_id, group_id) == 0:
                Members.objects.get(groupID=group_id, userID=user_id).delete()
                if Members.objects.filter(groupID=group_id).count() == 0:
                    Group.objects.get(groupID=group_id).delete()
                return Response({'message': 'User deleted successfully.'})
            else:
                return Response({'message': 'The settlement has not been completed'}, status=status.HTTP_402_PAYMENT_REQUIRED)
        except MyUser.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'message': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'message': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def DebtandCreditforMemberinGroup(user_id, group_id):
    list_buyer = buyer.objects.filter(userID=user_id, buy__groupID=group_id).distinct()
    list_consumer = consumer.objects.filter(userID=user_id, buy__groupID=group_id).distinct()
    sum = 0
    for buy in list_buyer:
        sum += buy.percent
    for buy in list_consumer:
        sum -= buy.percent
    return sum
