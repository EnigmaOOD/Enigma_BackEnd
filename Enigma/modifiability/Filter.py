from abc import ABC, abstractmethod
from unittest import result
from Group.models import Group, Members
from MyUser.models import MyUser
from buy.models import buy, buyer, consumer


class FilterInterface(ABC):
    @abstractmethod
    def FilterByUser(user_id, table):
        pass

    @abstractmethod
    def FilterByGroup(group_id, table):
        pass

    @abstractmethod
    def FilterByBoth(user_id, group_id, table):
        pass


class Filter(FilterInterface):
    def FilterByUser(user_id, table):
        if table == "buy":
            result = buy.objects.filter(userID=user_id)
        elif table == "Members":
            result = Members.objects.filter(userID=user_id)
        elif table == "Group":
            result = Group.objects.filter(userID=user_id)
        elif table == "MyUser":
            result = MyUser.objects.filter(userID=user_id)

        return result

    def FilterByGroup(group_id, table):
        if table == "buy":
            result = buy.objects.filter(groupID=group_id)
        elif table == "Members":
            result = Members.objects.filter(groupID=group_id)
        elif table == "Group":
            result = Group.objects.filter(groupID=group_id)
        elif table == "MyUser":
            result = MyUser.objects.filter(groupID=group_id)
        return result

    def FilterByBoth(user_id, group_id, table):
        if table == "buy_Buyer":
            result = buy.objects.filter(Buyers__userID=user_id, groupID=group_id).distinct()
        if table == "buy_consumer":
            result= buy.objects.filter(consumers__userID=user_id, groupID=group_id).distinct()
