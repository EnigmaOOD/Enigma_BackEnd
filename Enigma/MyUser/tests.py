import json
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from MyUser.models import MyUser
from Group.models import Group, Members
from buy.models import buy, buyer, consumer
from .serializers import UpdateUserSerializer, ChangePasswordSerializer

class RegisterAndAuthenticateTest(APITestCase):

    def authenticate(self):
        user_info = {
        "email":"u@u.com",
        "password":123 ,
        "name":"Uali",
        "picture_id" :10}
        
        self.client.post(('/auth/register/'),user_info)
        response = self.client.post(('/auth/token/'), {"username":"u@u.com","password":123})

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])

    def test_should_not_register_invalid_email(self):
        user_info = {
        "email":"uu.com",
        "password":123 ,
        "name":"Uali",
        "picture_id" :10}
        
        response = self.client.post(('/auth/register/'),user_info)
        self.assertEqual(response.status_code, 400)
        
    def test_should_not_register_invalid_password(self):
        user_info = {
        "email":"uu.com",
        "password":"",
        "name":"Uali",
        "picture_id" :10}
        
        response = self.client.post(('/auth/register/'),user_info)
        self.assertEqual(response.status_code, 400)

    def test_should_register(self):
        user_info = {
        "email":"u@u.com",
        "password":"usER!@123",
        "name":"Uali",
        "picture_id" :10}
        
        response = self.client.post(('/auth/register/'),user_info)
        self.assertEqual(response.status_code, 201)


    def test_should_get_token(self):
        user_info = {
        "email":"u@u.com",
        "password":"usER!@123",
        "name":"Uali",
        "picture_id" :10}
        
        self.client.post(('/auth/register/'),user_info)
        response = self.client.post(('/auth/token/'), {"username":"u@u.com",
                                                       "password":'usER!@123'})

        self.assertEqual(response.status_code, 200)

    def test_should_not_get_token_invalid_username(self):
        user_info = {
        "email":"u@u.com",
        "password":"usER!@123",
        "name":"Uali",
        "picture_id" :10}
        self.client.post(('/auth/register/'),user_info)
        response = self.client.post(('/auth/token/'), {"username":"u@a.com",
                                                       "password":'usER!@123'})
        self.assertEqual(response.status_code, 400)

    def test_should_not_get_token_invalid_password(self):
        user_info = {
        "email":"u@u.com",
        "password":"usER!@123",
        "name":"Uali",
        "picture_id" :10}
        
        self.client.post(('/auth/register/'),user_info)
        response = self.client.post(('/auth/token/'), {"username":"u@u.com",
                                                       "password":'usER!@12'})
        self.assertEqual(response.status_code, 400)

class EditProfileTest(APITestCase):

    def setUp(self):
        self.user = MyUser.objects.create(email='test@example.com', name='test', password='test', picture_id=15)
        self.client.force_authenticate(user=self.user)
        self.url = '/auth/EditProfile/'
        self.valid_payload = {
            'name': 'John Doe',
            'picture_id': 15,
        }
    
    def test_post_without_authentication(self):
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile_successfully(self):
        data = {
            'name': 'new name',
            'picture_id': 1
        }
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['picture_id'], data['picture_id'])
    
    def test_update_profile_non_data(self):
        response = self.client.put(self.url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"non_field_errors":["Either name or picture_id must be provided"]})

    def test_update_profile_just_name(self):
        data = {'name': 'new name'}
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['picture_id'], self.user.picture_id)

    def test_update_profile_just_pictureID(self):
        data = {'picture_id': 10}
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.user.name)
        self.assertEqual(response.data['picture_id'], data['picture_id'])

    def test_update_profile_pictureID_is_nagative(self):
        data = {
            'name': 'new name',
            'picture_id': -1
        }
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"picture_id":["Ensure this value is greater than or equal to 0."]})
        self.assertNotEqual(data['name'], self.user.name)
        self.assertNotEqual(data['picture_id'], self.user.picture_id)

    def test_update_profile_pictureID_is_more_than_values(self):
        data = {
            'name': 'new name',
            'picture_id': 22,
        }
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"picture_id":["Ensure this value is less than or equal to 21."]})
        self.assertNotEqual(data['name'], self.user.name)
        self.assertNotEqual(data['picture_id'], self.user.picture_id)
    
    def test_edit_profile_with_email_that_is_not_permission(self):
        data = {'email': 'test1@example.com'}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"non_field_errors":["Either name or picture_id must be provided"]})

    def test_edit_profile_with_password(self):
        data = {'password': 'new'}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"non_field_errors":["Either name or picture_id must be provided"]})

    def test_serializer_validations(self):
        serializer = UpdateUserSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), {'non_field_errors'})

class DeleteUser(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = MyUser.objects.create(email='test1@example.com', name='test1', password='test1')
        self.user2 = MyUser.objects.create(email='test2@example.com', name='test2', password='test2')
        self.user3 = MyUser.objects.create(email='test3@example.com', name='test3', password='test3')
        
        self.member1 = Members.objects.create(userID = self.user1, groupID=self.group)
        self.member2 = Members.objects.create(userID = self.user2, groupID=self.group)
        self.member3 = Members.objects.create(userID = self.user3, groupID=self.group)

        self.buy1 = buy.objects.create(groupID= self.group.id, cost=85000, date= "2023-02-01", picture_id= 1)
        self.buy1_buyer1 = buyer.objects.create(buy=self.buy1, userID=self.user1, percent=40000)
        self.buy1_buyer2 = buyer.objects.create(buy=self.buy1, userID=self.user2, percent=45000)
        self.buy1_consumer1 = consumer.objects.create(buy=self.buy1, userID=self.user1, percent=30000)
        self.buy1_consumer2 = consumer.objects.create(buy=self.buy1, userID=self.user2, percent=35000)
        self.buy1_consumer3 = consumer.objects.create(buy=self.buy1, userID=self.user3, percent=20000)

        self.buy2 = buy.objects.create(groupID= self.group.id, cost=400000, date= "2023-02-02", picture_id= 2)
        self.buy2_buyer1 = buyer.objects.create(buy=self.buy2, userID=self.user1, percent=400000)
        self.buy2_consumer1 = consumer.objects.create(buy=self.buy2, userID=self.user1, percent=300000)
        self.buy2_consumer2 = consumer.objects.create(buy=self.buy2, userID=self.user2, percent=100000)

        self.buy3 = buy.objects.create(groupID= self.group.id, cost=90000, date= "2023-02-03", picture_id= 3)
        self.buy3_buyer1 = buyer.objects.create(buy=self.buy3, userID=self.user2, percent=200000)
        self.buy3_consumer1 = consumer.objects.create(buy=self.buy3, userID=self.user2, percent=110000)
        self.buy3_consumer2 = consumer.objects.create(buy=self.buy3, userID=self.user2, percent=90000)

        self.url = '/auth/DeleteUser/'
        self.group = Group.objects.create(name='Test Group', currency='تومان')

    # def test_delete_user_from_group_successfully(self):
        