from abc import ABC, abstractmethod
from Group.models import Group, Members
import logging
logger = logging.getLogger('django')

class UserGroupInterface(ABC):
    @abstractmethod
    def group(user_id):
        pass

class userGroup(UserGroupInterface):

    def group(user_id):
            user_groups = Members.objects.filter(userID=user_id).values_list('groupID', flat=True)
            groups = Group.objects.filter(pk__in=user_groups)
            groups_count = groups.count()

            if groups_count>0:
                group_list = [{'id': group.id, 'name': group.name,
                           'currency': group.currency} for group in groups]
               
                logger.info('Groups retrieved successfully for User ID : {}'.format(user_id))
                logger.debug('Number of groups retrieved: {}'.format(groups_count))

                return ({'groups': group_list})
            else:
                return ({'Error': "User does not belong to any groups"})

