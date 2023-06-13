from abc import ABC, abstractmethod
from urllib import response
from rest_framework import status
from Group.models import Group, Members
import logging
from Group.serializers import GroupSerializer
logger = logging.getLogger('django')

class InfoInterface(ABC):
    @abstractmethod
    def Information(user_id, group_id):
        pass

class Info(InfoInterface):

    @staticmethod
    def Information(user_id, group_id):
        group = Group.objects.get(id=group_id)

        if not Members.objects.filter(groupID=group_id, userID=user_id).exists():
            logger.warning('User is not a member of the group. Group ID: {}'.format(group_id))
            return response({'error': 'User is not a member of the group.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = GroupSerializer(group)
        return group