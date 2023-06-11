from abc import ABC, abstractmethod
import logging
from Group.models import Group, Members
from buy.models import buyer, consumer

logger = logging.getLogger('django')

class DebtAndCreditForMember(ABC):
    @abstractmethod
    def DebtandCreditforMemberinGroup(user_id, group_id):
        pass

class DebtAndCreditCalculate(DebtAndCreditForMember):

    @staticmethod
    def DebtandCreditforMemberinGroup(user_id, group_id):
        try:
            if not (Group.objects.filter(id=group_id).exists()):
                logger.warning(f"DebtandCreditforMemberinGroup_Group not found. (groupID:{group_id})")
                return 'Group not found.'

            if not Members.objects.filter(groupID=group_id, userID=user_id).exists():
                logger.warning(f"DebtandCreditforMemberinGroup_User not found. (userID:{user_id})")
                return 'User not found.'

            list_buyer = buyer.objects.filter(userID=user_id, buy__groupID=group_id).distinct()
            list_consumer = consumer.objects.filter(userID=user_id, buy__groupID=group_id).distinct()
            total_sum = 0
            for buy in list_buyer:
                total_sum += buy.percent
            for buy in list_consumer:
                total_sum -= buy.percent
            return total_sum
        except Exception as e:
            logger.warning(f"DebtandCreditforMemberinGroup_Error occurred: {str(e)}")
            return str(e)
