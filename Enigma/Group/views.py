from asyncio.log import logger
from asyncio.windows_events import NULL

from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import status

from Group.models import Group, Members
from buy.models import buyer, consumer
from MyUser.models import MyUser
from .serializers import GroupSerializer, MemberSerializer
from .permissions import IsGroupUser
import logging

import json
import dependencies

logger = logging.getLogger('django')

class CreateGroup(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.info("Request received: POST group/CreateGroup")
        logger.info("User is authenticated.")

        serializer_data = GroupSerializer(data=request.data)
        if serializer_data.is_valid():
            logger.info("Validating group data.")

            new_group = serializer_data.save()
            group_id = new_group.id
            data = {}
            data["groupID"] = group_id
            data['emails'] = request.data.get('emails', [])
            data["emails"].append(str(self.request.user.email))

            logger.info("Sending request to add users to the group.")
            AddUserGroup.post(self=self, data=data)
            ans = AddUserGroup.post(self=self, data=data)
            if ans.status_code == 404:
                logger.error(f'User not found.Removing the newly created group. Group ID: {group_id}')
                Group.objects.last().delete()
                return Response({'message': 'user not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            logger.info(f'Group create successfully. Group ID: {group_id}')
            return Response(status=status.HTTP_201_CREATED)
        
        logger.error('Invalid group data.')
        return Response(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)


class AddUserGroup(APIView):
    permission_classes = [permissions.IsAuthenticated and IsGroupUser]

    def post(self, data):
        logger.info("Request received to add users to a group.: POST group/AddUserGroup")
        logger.info("User is authenticated.")

        if not isinstance(data, dict):
            data = data.data
        serializer_data = MemberSerializer(data=data)
        if serializer_data.is_valid():
            logger.info("Validating group data.")

            emails = data.get('emails', [])
            group_id = data.get('groupID')
            group = Group.objects.get(id=group_id)
            logger.info(f"Found group with ID:{group_id}")
            
            for emailUser in emails:
                try:
                    user = MyUser.objects.get(email=emailUser)
                    if not Members.objects.filter(groupID=group, userID=user).exists():
                        member = Members(groupID=group, userID=user)
                        member.save()
                    logger.info(f'Add user with email:{emailUser} to the group:{group_id}')

                except MyUser.DoesNotExist:
                    logger.error(f'User with email:{emailUser} not found.')
                    return Response({'message': 'user not found.'}, status=status.HTTP_404_NOT_FOUND)
                
            logger.info(f"Users added to group:{group_id} successfully.")
            return Response(status=status.HTTP_200_OK)
        
        logger.error("Invalid member data.")
        return Response(serializer_data.errors)
    
    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            logger.error(f"Permission deneid: {str(exc)}")
            return Response({'message': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)


class ShowGroups(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            
            user_id=self.request.user.user_id
            #group_list=dependencies.....

            return Response(group_list)
            
            #else:
            #    return Response({'Error': "User does not belong to any groups"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShowMembers(APIView):
    permission_classes = [permissions.IsAuthenticated and IsGroupUser]

    def post(self, request):
        try:
            group_id = request.data['groupID']

            cache_key = f"show_members_{group_id}"
            cached_data = dependencies.cache_servise_instance.get(cache_key)
            if cached_data:
                logger.info('Members retrieved successfully from cache for Group ID: {}'.format(group_id))
                cached_data = json.loads(cached_data)
                return Response(cached_data, status=status.HTTP_200_OK)

            #serializer = dependencies......           

            # Cache the data for future requests
            dependencies.cache_servise_instance.set(cache_key, serializer.data, 3600)

            logger.info('Members retrieved successfully for Group ID: {}, Group Members: {}'.format(group_id, serializer.data))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error('An error occurred while retrieving members for Group ID: {}'.format(group_id))
            logger.error('Error: {}'.format(str(e)))
            return Response({'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupInfo(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            user_id = request.user.user_id
            group_id = request.data.get('groupID')

            cache_key = f"group_info:{group_id}"
            cached_data = dependencies.cache_servise_instance.get(cache_key)
            if cached_data:
                logger.info('GroupInfo retrieved successfully from cache for Group ID: {}'.format(group_id))
                cached_data = json.loads(cached_data)
                return Response(cached_data, status=status.HTTP_200_OK)

            #serializer = dependencies......

            dependencies.cache_servise_instance.set(cache_key, serializer.data, 3600)

            logger.info('Group info retrieved successfully. Group ID: {}. Group name: {}'.format(group_id, serializer.data['name']))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            logger.error('Group not found. Group ID: {}'.format(group_id))
            return Response({'message': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
        except:
            logger.error('An error occurred while retrieving group info. Group ID: {}'.format(group_id))
            return Response({'message': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DeleteGroup(APIView):
    permission_classes = [permissions.IsAuthenticated and IsGroupUser]

    def post(self, request):
        
        try:
            group_id = request.data.get('groupID')
            group = Group.objects.get(id=group_id)
            group.delete()
            logger.info('Group deleted successfully. Group ID: {}'.format(group_id))
            logger.info(request.user.email + " delete the group")
            return Response({'message': 'Group deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e :
            logger.error('An error occurred: {}'.format(str(e)))
            return Response({'message': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


