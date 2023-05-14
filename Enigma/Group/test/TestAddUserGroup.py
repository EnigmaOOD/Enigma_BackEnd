from django.test import TestCase
from django.urls import reverse
from rest_framework import status, permissions
from rest_framework.test import APIClient
from unittest.mock import patch
import json
from ..models import Group, MyUser, Members
from ..serializers import MemberSerializer
from ..views import AddUserGroup
from ..permissions import IsGroupUser


class AddUserGroupTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user1 = MyUser.objects.create(email='test1@example.com', name='test1', password='test1')
        self.user2 = MyUser.objects.create(email='test2@example.com', name='test2', password='test2')
        self.user3 = MyUser.objects.create(email='test3@example.com', name='test3', password='test3')
        self.url = '/group/AddUserGroup/'
        self.group = Group.objects.create(name='Test Group', currency='تومان')
        # self.data = {'groupID': self.group.id, 'emails': ['test2@example.com', 'test3.example.com']}
        # self.invalid_data = {'groupID': 'invalid', 'emails': ['invalid']}
        self.view = AddUserGroup.as_view()

    def test_add_user_group_with_valid_data(self):
        self.client.force_authenticate(user=self.user1)
        Members.objects.create(userID=self.user1, groupID=self.group)
        data = {
            "groupID": self.group.id, 
            "emails": ["test2@example.com", "test3@example.com"]
        }
        response = self.client.post(self.url, data=data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Members.objects.count(), 3)
        self.assertEqual(Members.objects.first().userID, self.user1)
        self.assertEqual(Members.objects.last().userID, self.user3)
        self.assertTrue(Members.objects.get(userID=self.user2))

    def test_add_user_group_with_invalid_email(self):
        self.client.force_authenticate(user=self.user1)
        Members.objects.create(userID=self.user1, groupID=self.group)
        data = {
            "groupID": self.group.id, 
            "emails": ["test2@example.com", "test3.example.com", "test3@example.com"]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {"message":"user not found."})
        self.assertEqual(Members.objects.count(), 2)
        self.assertEqual(Members.objects.first().userID, self.user1)
        self.assertEqual(Members.objects.last().userID, self.user2)

    def test_add_user_group_with_not_email(self):
        self.client.force_authenticate(user=self.user2)
        Members.objects.create(userID=self.user2, groupID=self.group)
        data = {
            "groupID": self.group.id, 
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Members.objects.count(), 1)

    def test_add_user_group_with_valid_email_but_is_not_register(self):
        self.client.force_authenticate(user=self.user3)
        Members.objects.create(userID=self.user3, groupID=self.group)
        data = {
            'groupID': self.group.id,
            "emails": ["test1@example.com","miss_ramazani@yahoo.com","test2@example.com"]
        }
        response = self.client.post(self.url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {"message":"user not found."})
        self.assertEqual(Members.objects.count(), 2)

    def test_add_user_group_with_valid_email_but_is_duplicate(self):
        self.client.force_authenticate(user=self.user1)
        Members.objects.create(userID=self.user1, groupID=self.group)
        data = {
            'groupID': self.group.id,
            "emails": ["test1@example.com"]
        }
        response = self.client.post(self.url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Members.objects.count(), 1)

    def test_add_user_group_with_invalid_user(self):
        self.client.force_authenticate(user=self.user2)
        Members.objects.create(userID=self.user1, groupID=self.group)
        data = {
            'groupID': self.group.id,
            "emails": ["test1@example.com","miss_ramazani@yahoo.com","test2@example.com"]
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_add_user_group_with_invalid_serializer_data(self):
    #     self.client.force_authenticate(user=self.user2)
    #     Members.objects.create(userID=self.user2, groupID=self.group)
    #     data = {
    #         'groupID': self.group.id,
    #         "emails": ["test1@example.com", "test2@example.com"]
    #     }
    #     serializer_data = MemberSerializer(data=data)
    #     serializer_data.is_valid(raise_exception=True)
    #     response = self.client.post(self.url, data=serializer_data.data)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertEqual(response.data, serializer_data._errors)

    def test_add_user_group_with_non_data(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content), {"message":"You do not have permission to perform this action."})

