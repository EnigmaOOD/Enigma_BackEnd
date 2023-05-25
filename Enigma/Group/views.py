from asyncio.log import logger

from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import status
from Group.models import Group, Members
from buy.models import buyer, consumer
from .serializers import GroupSerializer, MemberSerializer, AmountDebtandCreditMemberSerializer, ShowMemberSerializer
from MyUser.models import MyUser
from .permissions import IsGroupUser
import logging

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
            try:
                group = Group.objects.get(id=group_id)
                logger.info(f"Found group with ID:{group_id}")

            except Group.DoesNotExist:
                logger.error(f"Group with ID:{group_id} not found.")
                return Response({'message': 'group not found.'}, status=status.HTTP_404_NOT_FOUND)
            
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
            user_groups = Members.objects.filter(
                userID=self.request.user.user_id).values_list('groupID', flat=True)
            groups = Group.objects.filter(pk__in=user_groups)
            groups_count = groups.count()

            if groups_count>0:
                group_list = [{'id': group.id, 'name': group.name,
                           'currency': group.currency} for group in groups]
               
                logger.info('Groups retrieved successfully for User ID : {}'.format(self.request.user.user_id))
                logger.debug('Number of groups retrieved: {}'.format(groups_count))

                return Response({'groups': group_list})
            else:
                return Response({'Error': "User does not belong to any groups"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShowMembers(APIView):
    permission_classes = [permissions.IsAuthenticated and IsGroupUser]

    def post(self, request):
        try:
            cost=[]
            group_id=request.data['groupID']
            members = Members.objects.filter(groupID=request.data['groupID'])
            logger.debug('Number of members retrieved: {}'.format(len(members)))

            for member in members:
                member_id = member.userID.user_id

                 # Call dobet function to get cost for this member
                cost.append(DebtandCreditforMemberinGroup(self.request.user, group_id)) 
            serializer = ShowMemberSerializer(members, many=True)
            for member in reversed(serializer.data):
                member['cost'] = cost.pop()
           
            logger.info('Members retrieved successfully for Group ID: {}, Group Members: {}'.format(request.data['groupID'], serializer.data))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error('An error occurred while retrieving members for Group ID: {}'.format(request.data['groupID']))
            logger.error('Error: {}'.format(str(e)))

            return Response({'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupInfo(APIView):
    permission_classes = [permissions.IsAuthenticated ]

    def post(self, request):
        try:
            user_id = request.user.user_id
            group_id = request.data.get('groupID')
            group = Group.objects.get(id=group_id)

            if not Members.objects.filter(groupID=group_id, userID=user_id).exists():
                logger.warning('User is not a member of the group. Group ID: {}, User email : {}'.format(group_id, request.user.email))
                return Response({'error': 'User is not a member of the group.'}, status=status.HTTP_403_FORBIDDEN)


            serializer = GroupSerializer(group)
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
    


def DebtandCreditforMemberinGroup(user_id, group_id):
    try:
        if not (Group.objects.filter(id = group_id).exists()):
            logger.warning(f"DebtandCreditforMemberinGroup_Group not found.(groupID:{group_id})")
            return 'Group not found.'

        if not Members.objects.filter(groupID = group_id, userID=user_id).exists():
            logger.warning(f"DebtandCreditforMemberinGroup_User not found.(userID:{user_id})")
            return 'User not found.'
        
        list_buyer = buyer.objects.filter(userID=user_id, buy__groupID=group_id).distinct()
        list_consumer = consumer.objects.filter(userID=user_id, buy__groupID=group_id).distinct()
        sum = 0
        for buy in list_buyer:
            sum += buy.percent
        for buy in list_consumer:
            sum -= buy.percent
        return sum
    except Exception as e:
        logger.warning(f"DebtandCreditforMemberinGroup_Error occurred:{str(e)}")
        return str(e)
