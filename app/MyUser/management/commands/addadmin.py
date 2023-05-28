import random
from Group.models import Group, Members
import faker.providers
from django.core.management.base import BaseCommand
from faker import Faker
import faker.providers
from MyUser.models import MyUser
from fake_persian_name import fake_name as fpn
from buy.models import buy,buyer,consumer

class Command(BaseCommand):
    help = "Command information"

    def handle(self, *args, **kwargs):

        admin_user = MyUser.objects.get(email="a@a.com")
        groups = Group.objects.all()
        for group in groups:
            print(group.name)
            Members.objects.create(userID=admin_user, groupID=group)
        return