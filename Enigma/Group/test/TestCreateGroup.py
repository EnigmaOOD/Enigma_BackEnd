import json
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Group, Members
from ..serializers import GroupSerializer
from MyUser.models import MyUser

class TestCreateGroup(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user1 = MyUser.objects.create(email='test1@example.com', password='test1', name='test1', picture_id=1)
        self.user2 = MyUser.objects.create(email='test2@example.com', password='test2', name='test2', picture_id=2)
        self.user3 = MyUser.objects.create(email='test3@example.com', password='test3', name='test3', picture_id=3)

    def test_create_group(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 1,
            'emails': ["test2@example.com","test3@example.com"]
        }
        response = self.client.post('/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Group.objects.count(), 1)
        group = Group.objects.first()
        self.assertEqual(group.name, 'Test Group')
        self.assertEqual(group.currency, 'تومان')
        self.assertEqual(group.picture_id, 1)

        members = Members.objects.filter(groupID=group)
        self.assertEqual(members.count(), 3)
        self.assertEqual(members.first().userID, self.user2)
        self.assertEqual(members.last().userID, self.user1)
        self.assertTrue(members.get(userID=self.user3))

    def test_create_group_name_is_null(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': '',
            'currency': 'تومان',
            'picture_id': 1,
            'emails': ["test2@example.com","test3@example.com"]
        }
        response = self.client.post('/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"name":["This field may not be blank."]})
        self.assertEqual(Group.objects.count(), 0)

    def test_create_group_name_is_space(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': '         ',
            'currency': 'تومان',
            'picture_id': 1,
            'emails': ["test2@example.com","test3@example.com"]
        }
        response = self.client.post('/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"name":["This field may not be blank."]})
        self.assertEqual(Group.objects.count(), 0)

    def test_create_group_description_is_null(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 1,
            'emails': ["test2@example.com","test3@example.com"]
        }
        response = self.client.post('/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 1)

    def test_create_group_currency_is_null(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Test Group',
            'currency': '',
            'picture_id': 1,
            'emails': ["test2@example.com","test3@example.com"]
        }
        response = self.client.post('/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"currency":["This field may not be blank."]})
        self.assertEqual(Group.objects.count(), 0)
    
    def test_create_group_pictureID_is_null(self):
        self.client.force_authenticate(user=self.user2)
        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'emails': ["test1@example.com","test3@example.com"]
        }
        response = self.client.post('/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 1)
    
    def test_create_group_pictureID_is_nagative(self):
        self.client.force_authenticate(user=self.user2)
        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': -1,
            'emails': ["test1@example.com","test3@example.com"]
        }
        response = self.client.post('/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"picture_id":["Ensure this value is greater than or equal to 0."]})
        self.assertEqual(Group.objects.count(), 0)

    def test_create_group_pictureID_is_more_than_values(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 4,
            'emails': ["test2@example.com","test3@example.com"]
        }
        response = self.client.post('/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"picture_id":["Ensure this value is less than or equal to 3."]})
        self.assertEqual(Group.objects.count(), 0)

    def test_create_group_not_email(self):
        self.client.force_authenticate(user=self.user2)
        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 3,
        }
        response = self.client.post('/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 1)

        members = Members.objects.filter(groupID=Group.objects.first())
        self.assertEqual(members.count(), 1)
        self.assertEqual(members.first().userID, self.user2)

    def test_create_group_valid_email_but_is_not_register(self):
        self.client.force_authenticate(user=self.user2)
        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 3,
            "emails": ["test3@example.com","miss_ramazani@yahoo.com","nourieh110@gmail"]
        }
        response = self.client.post('/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {"message":"user not found."})
        self.assertEqual(Group.objects.count(), 0)
    
    def test_create_group_invalid_email(self):
        self.client.force_authenticate(user=self.user2)
        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 3,
            "emails": ["test3@example.com","miss_ramazani","nourieh110gmail"]
        }
        response = self.client.post('/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {"message":"user not found."})
        self.assertEqual(Group.objects.count(), 0)

    # اگر می خواین ارور ایمیل نامعتبر تغییر کند بگویید