from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework import permissions, generics
from rest_framework.exceptions import ValidationError
from .models import MyUser
from Group.models import Group, Members
from .serializers import MyUserSerializer, UpdateUserSerializer
from rest_framework import permissions, generics
from rest_framework.exceptions import ValidationError
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import MyUser
from Group.models import Group, Members
from buy.models import buyer, consumer
from .serializers import MyUserSerializer, UpdateUserSerializer
from .utils import Util

import logging
import json
import dependencies



logger = logging.getLogger('django')


class RegisterUser(generics.GenericAPIView):

    permission_classes = [permissions.AllowAny]

    serializer_class = MyUserSerializer

    def post(self, request):
        logger.info("Request received: POST auth/register")

        user = request.data 
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("User register successfully.")

        user_data = serializer.data
        user = MyUser.objects.get(email=user_data['email'])
        token, created = Token.objects.get_or_create(user=user)

        current_site = get_current_site(request).domain
        relativeLink=reverse('verify-email')
        
        absurl = 'http://' + current_site + relativeLink+"?token="+str(token)
        email_body ='Hi '+user.name+' Use link below to verify your email \n'+absurl
        data = {'email_body':email_body, 'email_subject':'Verify your email', 'to_email':[user.email]}
        logger.info(f"Sending verification email to the user.(email_body:{email_body})")
        Util.send_email(data)

        logger.info(f"User registration completed.(email:{user.email}, name:{user.name})")
        return Response(user_data, status=status.HTTP_201_CREATED)  

class VerifyEmail(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        logger.info("Request received: GET auth/verify-email")
        token = request.query_params.get('token')
        if token:
            logger.info(f"Token parameter found: {token}")
            try:
                user = Token.objects.get(key=token).user
                user.is_active = True
                user.save()
                logger.info(f"Email verified successfully for user: {user.email}")
                return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
            
            except Token.DoesNotExist:
                logger.warning(f"Invalid token: {token}")
                return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.info(f"Token parameter is missing: {token}")
            return Response({'error': 'Token parameter is missing.'}, status=status.HTTP_400_BAD_REQUEST)




"""
class ChangePasswordView(generics.UpdateAPIView):

    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
"""

class EditProfile(UpdateAPIView):
    
    users = MyUser.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer

    def get_object(self):
        logger.info("Retrieving user object.")
        return self.request.user

    def perform_update(self, serializer):
        logger.info("Request received to edit profile.: PUT auth/EditProfile")
        logger.info("User is authenticated.")

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user)
        except ValidationError as e:
            logger.warning(f"Validation error occurred: {str(e)}")
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"User:{self.request.user.pk} data updated successfully.(name:{self.request.user.name}, picture_id:{self.request.user.picture_id})")
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserInfo(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            #if not MyUser.objects.filter(pk=user.pk).exists():
            
            if not dependencies.filter_servise_instance.FilterByUser(user.pk, "MyUser").exists():
                logger.error('User not found. User ID: {}'.format(user.user_id))
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            cache_key = f"user_info:{user.user_id}"
            cached_data = dependencies.cache_servise_instance.get(cache_key)
            if cached_data:
                logger.info('UserInfo retrieved successfully from cache for Group ID: {}'.format(user.user_id))
                cached_data = json.loads(cached_data)
                return Response(cached_data, status=status.HTTP_200_OK)

            #cache_key = f"user_info:{user.user_id}"
            #redis_conn = get_redis_connection()
            #cached_data = redis_conn.get(cache_key)
            #if cached_data:
                # If cached data exists, return it
            #    user_info = json.loads(cached_data.decode())
            #else:

            user_info = {
                'user_id': user.user_id,
                'email': user.email,
                'name': user.name,
                'picture_id': user.picture_id,
                'is_active': user.is_active,
                'is_admin': user.is_admin,
                'is_staff': user.is_staff,
            }
            dependencies.cache_servise_instance.set(cache_key, user_info, 3600)
            #    redis_conn.set(cache_key, json.dumps(user_info))
            #   redis_conn.expire(cache_key, 3600)  # Set expiration time for 1 hour (3600 seconds)

            logger.info('User information retrieved successfully. User ID: {}, Email: {}'.format(user.user_id, user.email))
            logger.debug('User information: {}'.format(user_info))
            return Response(user_info)
        
        except Exception as e:
            logger.error('An error occurred while retrieving user information. User ID: {}, Email: {}'.format(user.user_id, user.email))
            logger.error('Error: '+ str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LeaveGroup(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.info("Request received to leave group.: POST auth/LeaveGroup")
        logger.info("User is authenticated.")

        try:
            group_id = request.data['groupID']
            logger.info(f"Group ID:{group_id} for leave group")

            result = dependencies.debtandcredit_calculate_servise_instance.DebtandCreditforMemberinGroup(self.request.user, group_id)
            if isinstance(result, str):
                if result == 'Group not found.':
                     logger.error(f"Error: {result}")
                     return Response({'message': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)       
                if result == 'User not found.':
                     logger.error(f"Error: {result}")
                     return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
                else:
                     logger.error(f"Error: {result}")
                     return Response({'message': result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            if result == 0:
                Members.objects.get(groupID=group_id, userID=self.request.user).delete()
                if Members.objects.filter(groupID=group_id).count() == 0:
                    logger.info(f" No more members in the group. Deleting the group. (groupID: {group_id})")
                    Group.objects.get(groupID=group_id).delete()

                logger.info(f"User deleted successfully. (userID:{self.request.user}, groupID:{group_id})")
                return Response({'message': 'User deleted successfully.'}, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Settlement not completed. (userID:{self.request.user}, groupID:{group_id})")
                return Response({'message': 'The settlement has not been completed'}, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


