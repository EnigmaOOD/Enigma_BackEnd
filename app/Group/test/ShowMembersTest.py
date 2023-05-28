from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from Group.models import Group, Members
from MyUser.models import MyUser
from unittest import mock
from unittest.mock import patch
from Group.serializers import ShowMemberSerializer

class ShowMembersTests(APITestCase):
    def setUp(self):
        self.group = Group.objects.create(name='Test Group', currency='USD')
        self.user1 = MyUser.objects.create(email='test1@test.com', password='testpass')
        self.user2 = MyUser.objects.create(email='test2@test.com', password='testpass')
        self.user3 = MyUser.objects.create(email='test3@test.com', password='testpass')

        Members.objects.create(userID=self.user1, groupID=self.group)
        Members.objects.create(userID=self.user2, groupID=self.group)

        self.url = '/group/ShowMembers/'

    def test_show_members_successful(self):
        self.client.force_authenticate(user=self.user1)
        data = {'groupID': self.group.id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_show_members_with_valid_group_id(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, data={'groupID': self.group.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['userID']['user_id'], self.user1.user_id)
        self.assertEqual(response.data[1]['userID']['user_id'], self.user2.user_id)
        self.assertEqual(response.data[0]['userID']['email'], self.user1.email)
        self.assertEqual(response.data[1]['userID']['email'], self.user2.email)

    def test_show_members_invalid_group(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, {'groupID': self.group.id+1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_show_members_wrong_user(self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(self.url, {'groupID': self.group.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_show_members_no_members(self):
        self.client.force_authenticate(user=self.user1)
        group = Group.objects.create(name='Empty Group', currency='USD')
        response = self.client.post(self.url, {'groupID': group.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_show_members_exception(self):
        self.client.force_authenticate(user=self.user1)
        with mock.patch('Group.views.DebtandCredit', side_effect=Exception('Test Exception')):
            response = self.client.post(self.url, {'groupID': self.group.id})
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data, {'Error': 'Test Exception'})
