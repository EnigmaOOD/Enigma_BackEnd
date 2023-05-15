from rest_framework.test import APITestCase
from rest_framework import status
from MyUser.models import MyUser
from unittest.mock import patch

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


    def test_should_not_get_token_email_not_verified(self):
        user_info = {
        "email":"u@u.com",
        "password":"usER!@123",
        "name":"Uali",
        "picture_id" :10}
        
        self.client.post(('/auth/register/'),user_info)
        response = self.client.post(('/auth/token/'), {"username":"u@u.com",
                                                       "password":'usER!@123'})

        self.assertEqual(response.status_code, 400)

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


# class UserInfoTestCase(APITestCase):
    
#     def setUp(self):
#         self.user = MyUser.objects.create(email='testuser@example.com', password='testpass', name='Test User')
#         self.url = '/auth/UserInfo/'
        
#     def test_user_info(self):
#         self.client.force_authenticate(user=self.user)
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['user_info']['user_id'], (self.user.user_id))
#         self.assertEqual(response.data['user_info']['email'], self.user.email)
#         self.assertEqual(response.data['user_info']['name'], self.user.name)
#         self.assertEqual(response.data['user_info']['picture_id'], self.user.picture_id)
#         self.assertEqual(response.data['user_info']['is_active'], self.user.is_active)
#         self.assertEqual(response.data['user_info']['is_admin'], self.user.is_admin)
#         self.assertEqual(response.data['user_info']['is_staff'], self.user.is_staff)
    


#     def test_user_info_admin_user(self):
#         self.user.is_admin = True
#         self.user.save()
#         self.client.force_authenticate(user=self.user)
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_user_info_staff_user(self):
#         self.user.is_staff = True
#         self.user.save()
#         self.client.force_authenticate(user=self.user)
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

    
#     def test_user_info_extra_fields(self):
#         self.client.force_authenticate(user=self.user)
#         # Add an extra field to the request data
#         response = self.client.post(self.url, data={'extra_field': 'extra_value'})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         # Check that the extra field is not present in the response
#         self.assertFalse('extra_field' in response.data['user_info'])
    
#     def test_user_info_nonexistent_user(self):
#         # Test that a nonexistent user returns a 404 Not Found error
#         self.client.force_authenticate(user=self.user)
#         self.user.delete()
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


#     def test_user_info_unauthenticated(self):
#         response = self.client.post(self.url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_user_info_put_method(self):
#         self.client.force_authenticate(user=self.user)
#         response = self.client.put(self.url)
#         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

#     def test_post_exception(self):
#         self.client.force_authenticate(user=self.user)
#         with patch('MyUser.views.MyUser.objects.filter') as mock_filter:
#             mock_filter.side_effect = Exception('Something went wrong')
#             response = self.client.post(self.url)
        
#         # Check that the view returns a 500 error response with the expected error message
#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertEqual(response.data['error'], 'Something went wrong')