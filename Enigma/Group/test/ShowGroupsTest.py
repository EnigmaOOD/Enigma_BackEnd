
from rest_framework.test import APITestCase
from rest_framework import status
from Group.models import Group, Members
from MyUser.models import MyUser
from unittest import mock


class ShowGroupsTestCase(APITestCase):
    
    def setUp(self):
        self.user = MyUser.objects.create(email='testuser@test.local', password='testpass',  name='test', picture_id=4)
        self.url = '/group/ShowGroups/'

    def test_show_groups_success(self):
        self.client.force_authenticate(user=self.user)
        group = Group.objects.create(name='Test Group', currency='USD')
        Members.objects.create(userID=self.user, groupID=group)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['groups'], [{'id': group.id, 'name': group.name, 'currency': group.currency}])

    def test_show_user_groups_multiple_success(self):
        self.client.force_authenticate(user=self.user)
        group1 = Group.objects.create(name='Test Group 1', currency='USD')
        group2 = Group.objects.create(name='Test Group 2', currency='$')
        group3 = Group.objects.create(name='Test Group 3', currency='تومان')
        group4 = Group.objects.create(name='Test Group 4', currency='ریال')

        Members.objects.create(groupID=group1, userID=self.user)
        Members.objects.create(groupID=group2, userID=self.user)
        Members.objects.create(groupID=group3, userID=self.user)
        Members.objects.create(groupID=group4, userID=self.user)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['groups']), 4)
        self.assertEqual(response.data['groups'][0]['name'], 'Test Group 1')
        self.assertEqual(response.data['groups'][0]['currency'], 'USD')
        self.assertEqual(response.data['groups'][1]['name'], 'Test Group 2')
        self.assertEqual(response.data['groups'][1]['currency'], '$')
        self.assertEqual(response.data['groups'][2]['name'], 'Test Group 3')
        self.assertEqual(response.data['groups'][2]['currency'], 'تومان')
        self.assertEqual(response.data['groups'][3]['name'], 'Test Group 4')
        self.assertEqual(response.data['groups'][3]['currency'], 'ریال')


    def test_show_groups_no_groups(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'Error': 'User does not belong to any groups'})
   
    def test_show_groups_unauthenticated(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_show_groups_invalid_method(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_show_groups_exception(self):
        self.client.force_authenticate(user=self.user)
        with mock.patch('Group.views.Members.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception('test exception')
            response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, {'Error': 'test exception'})

    def test_show_groups_with_empty_DB(self):
        self.client.force_authenticate(user=self.user)
        Members.objects.all().delete()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Error', response.data)