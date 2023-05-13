from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

from ..models import Group, MyUser, Members
from ..serializers import MemberSerializer
from ..views import AddUserGroup


class AddUserGroupTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user1 = MyUser.objects.create(email='test1@example.com', name='test1', password='test1')
        self.user2 = MyUser.objects.create(email='test2@example.com', name='test2', password='test2')
        self.user3 = MyUser.objects.create(email='test3@example.com', name='test3', password='test3')
        self.group = Group.objects.create(name='Test Group', currency='تومان', picture_id=1)
        self.data = {'groupID': self.group.id, 'emails': ['test2@example.com', 'test3.example.com']}
        # self.invalid_data = {'groupID': 'invalid', 'emails': ['invalid']}
        self.serializer_data = MemberSerializer(data=self.data)
        self.view = AddUserGroup.as_view()

    def test_add_user_group_with_valid_data(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/group/AddUserGroup/', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Members.objects.count(), 3)
        # self.assertEqual(members.first().userID, self.user2)
        # self.assertEqual(members.last().userID, self.user1)
        # self.assertTrue(members.get(userID=self.user3))

    # def test_add_user_group_with_invalid_data(self):
    #     response = self.client.post(self.url, self.invalid_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # @patch('rest_framework.response.Response')
    # def test_add_user_group_with_invalid_user(self, mocked_response):
    #     MyUser.objects.filter(email='testuser@example.com').delete()
    #     mocked_response.return_value = Response({'message': 'user not found.'}, status=status.HTTP_404_NOT_FOUND)
    #     response = self.client.post(self.url, self.data, format='json')
    #     mocked_response.assert_called_once_with({'message': 'user not found.'}, status=status.HTTP_404_NOT_FOUND)
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_add_user_group_with_invalid_serializer_data(self):
    #     self.serializer_data.is_valid = lambda: False
    #     with patch('rest_framework.response.Response') as mocked_response:
    #         self.view(self.serializer_data)
    #         mocked_response.assert_called_once_with(self.serializer_data.errors)

    # def test_add_user_group_with_non_dict_data(self):
    #     response = self.client.post(self.url, [], format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_permission_classes(self):
    #     self.assertTrue(isinstance(self.view.permission_classes[0], permissions.IsAuthenticated))
    #     self.assertTrue(isinstance(self.view.permission_classes[1], IsGroupUser))

