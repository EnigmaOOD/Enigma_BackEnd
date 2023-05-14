import json
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import MyUser
from .serializers import UpdateUserSerializer, ChangePasswordSerializer

class RegisterAndAuthenticateTest(APITestCase):

    def authenticate(self):
        user_info = {
        "email":"u@u.com",
        "password":123 ,
        "name":"Uali",
        "picture_id" :10}
        
        self.client.post(('/auth/register/'),user_info)
        response = self.client.post(('/auth/token/'), {"username":"u@u.com",
                                                       "password":123})

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

    def test_update_profile_successfully(self):
        data = {
            'name': 'new name',
            'picture_id': 1
        }
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['picture_id'], data['picture_id'])

    def test_update_profile_just_name(self):
        data = {'name': 'new name'}
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['picture_id'], self.user.picture_id)

    # def test_update_profile_non_data(self):
    #     response = self.client.put(self.url, data={}, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

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
    
    # def test_edit_profile_with_email(self):
    #     data = {'email': 'test1@example.com'}
    #     response = self.client.put(self.url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_edit_profile_with_password(self):
    #     data = {'password': 'new'}
    #     response = self.client.put(self.url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_serializer_validations(self):
    #     serializer = UpdateUserSerializer(data={})
    #     print(serializer.is_valid())
    #     self.assertTrue(serializer.is_valid())
    #     self.assertEqual(set(serializer.errors.keys()), {'name', 'picture_id'})
