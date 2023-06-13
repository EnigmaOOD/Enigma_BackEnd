from abc import ABC, abstractmethod
from urllib import response
from rest_framework import status
from Group.models import Group, Members
import logging
from Group.serializers import ShowMemberSerializer
import dependencies
logger = logging.getLogger('django')

class CostInterface(ABC):
    @abstractmethod
    def cost(group_id):
        pass

class CostForMember(CostInterface):

    def cost(group_id):
        cost = []
        members = Members.objects.filter(groupID=group_id)
        logger.debug('Number of members retrieved: {}'.format(len(members)))
        debt = dependencies.debtandcredit_calculate_servise_instance
        for member in members:
           member_id = member.userID.user_id
           cost.append(debt.DebtandCreditforMemberinGroup(member_id, group_id))

        serializer = ShowMemberSerializer(members, many=True)

        for member in reversed(serializer.data):
            member['cost'] = cost.pop()
        
        return serializer