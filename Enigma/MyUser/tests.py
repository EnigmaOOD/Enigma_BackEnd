import json
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch

from MyUser.models import MyUser
from Group.models import Group, Members
from buy.models import buy, buyer, consumer

from MyUser.serializers import UpdateUserSerializer

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

class VerifyEmailTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = MyUser.objects.create(email='testuser@test.local', password='testpass',  name='test', picture_id=4)
        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.verify_email_url = reverse('verify-email')

    def test_verify_email_ok(self):
        user = self.user

        # Build the URL for verifying the email with the token
        
        url = f'{self.verify_email_url}?token={self.token}'
        # Send a GET request to the verification URL
        response = self.client.get(url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Retrieve the user from the database and assert that it is now active
        self.user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_verify_email_wrong_token(self):

        token = "Wrong"

        url = f'{self.verify_email_url}?token={token}'
        # Send a GET request to the verification URL
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)




class UserInfoTestCase(APITestCase):
    
    def setUp(self):
        self.user = MyUser.objects.create(email='testuser@example.com', password='testpass', name='Test User')
        self.url = '/auth/UserInfo/'
        
    def test_user_info(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_info']['user_id'], (self.user.user_id))
        self.assertEqual(response.data['user_info']['email'], self.user.email)
        self.assertEqual(response.data['user_info']['name'], self.user.name)
        self.assertEqual(response.data['user_info']['picture_id'], self.user.picture_id)
        self.assertEqual(response.data['user_info']['is_active'], self.user.is_active)
        self.assertEqual(response.data['user_info']['is_admin'], self.user.is_admin)
        self.assertEqual(response.data['user_info']['is_staff'], self.user.is_staff)
    


    def test_user_info_admin_user(self):
        self.user.is_admin = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_info_staff_user(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_user_info_extra_fields(self):
        self.client.force_authenticate(user=self.user)
        # Add an extra field to the request data
        response = self.client.post(self.url, data={'extra_field': 'extra_value'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the extra field is not present in the response
        self.assertFalse('extra_field' in response.data['user_info'])
    
    def test_user_info_nonexistent_user(self):
        # Test that a nonexistent user returns a 404 Not Found error
        self.client.force_authenticate(user=self.user)
        self.user.delete()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_user_info_unauthenticated(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_info_put_method(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_exception(self):
        self.client.force_authenticate(user=self.user)
        with patch('MyUser.views.MyUser.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception('Something went wrong')
            response = self.client.post(self.url)
        
        # Check that the view returns a 500 error response with the expected error message
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['error'], 'Something went wrong')


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

class LeaveGroup(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = MyUser.objects.create(email='test1@example.com', name='test1', password='test1')
        self.user2 = MyUser.objects.create(email='test2@example.com', name='test2', password='test2')
        self.user3 = MyUser.objects.create(email='test3@example.com', name='test3', password='test3')
        self.user4 = MyUser.objects.create(email='test4@example.com', name='test4', password='test4')

        self.group1 = Group.objects.create(name='Test Group1', currency='تومان')
        self.group2 = Group.objects.create(name='Test Group2', currency='تومان')

        self.group1_member1 = Members.objects.create(userID = self.user1, groupID=self.group1)
        self.group1_member2 = Members.objects.create(userID = self.user2, groupID=self.group1)
        self.group1_member3 = Members.objects.create(userID = self.user3, groupID=self.group1)

        self.group1_buy1 = buy.objects.create(groupID= self.group1, cost=85000, date= "2023-02-01", picture_id= 1, added_by=self.user1)
        self.group1_buy1_buyer1 = buyer.objects.create(buy=self.group1_buy1, userID=self.user1, percent=40000)
        self.group1_buy1_buyer2 = buyer.objects.create(buy=self.group1_buy1, userID=self.user2, percent=45000)
        self.group1_buy1_consumer1 = consumer.objects.create(buy=self.group1_buy1, userID=self.user1, percent=30000)
        self.group1_buy1_consumer2 = consumer.objects.create(buy=self.group1_buy1, userID=self.user2, percent=35000)
        self.group1_buy1_consumer3 = consumer.objects.create(buy=self.group1_buy1, userID=self.user3, percent=20000)

        self.group1_buy2 = buy.objects.create(groupID= self.group1, cost=400000, date= "2023-02-02", picture_id= 2, added_by=self.user1)
        self.group1_buy2_buyer1 = buyer.objects.create(buy=self.group1_buy2, userID=self.user1, percent=400000)
        self.group1_buy2_consumer1 = consumer.objects.create(buy=self.group1_buy2, userID=self.user1, percent=300000)
        self.group1_buy2_consumer2 = consumer.objects.create(buy=self.group1_buy2, userID=self.user2, percent=100000)

        self.group1_buy3 = buy.objects.create(groupID= self.group1, cost=90000, date= "2023-02-03", picture_id= 3, added_by=self.user2)
        self.group1_buy3_buyer1 = buyer.objects.create(buy=self.group1_buy3, userID=self.user2, percent=200000)
        self.group1_buy3_consumer1 = consumer.objects.create(buy=self.group1_buy3, userID=self.user2, percent=110000)
        self.group1_buy3_consumer2 = consumer.objects.create(buy=self.group1_buy3, userID=self.user3, percent=90000)

        self.group2_member1 = Members.objects.create(userID = self.user1, groupID=self.group2)
        self.group2_member2 = Members.objects.create(userID = self.user2, groupID=self.group2)
        self.group2_member3 = Members.objects.create(userID = self.user3, groupID=self.group2)

        self.group2_buy1 = buy.objects.create(groupID= self.group2, cost=85000, date= "2023-02-01", picture_id= 1, added_by=self.user1)
        self.group2_buy1_buyer1 = buyer.objects.create(buy=self.group2_buy1, userID=self.user1, percent=40000)
        self.group2_buy1_buyer2 = buyer.objects.create(buy=self.group2_buy1, userID=self.user2, percent=45000)
        self.group2_buy1_consumer1 = consumer.objects.create(buy=self.group2_buy1, userID=self.user1, percent=30000)
        self.group2_buy1_consumer2 = consumer.objects.create(buy=self.group2_buy1, userID=self.user2, percent=35000)
        self.group2_buy1_consumer3 = consumer.objects.create(buy=self.group2_buy1, userID=self.user3, percent=20000)

        self.group2_buy2 = buy.objects.create(groupID= self.group2, cost=400000, date= "2023-02-02", picture_id= 2, added_by=self.user1)
        self.group2_buy2_buyer1 = buyer.objects.create(buy=self.group2_buy2, userID=self.user1, percent=400000)
        self.group2_buy2_consumer1 = consumer.objects.create(buy=self.group2_buy2, userID=self.user1, percent=300000)
        self.group2_buy2_consumer2 = consumer.objects.create(buy=self.group2_buy2, userID=self.user2, percent=100000)

        self.group2_buy3 = buy.objects.create(groupID= self.group2, cost=90000, date= "2023-02-03", picture_id= 3, added_by=self.user2)
        self.group2_buy3_buyer1 = buyer.objects.create(buy=self.group2_buy3, userID=self.user3, percent=200000)
        self.group2_buy3_consumer1 = consumer.objects.create(buy=self.group2_buy3, userID=self.user1, percent=110000)
        self.group2_buy3_consumer2 = consumer.objects.create(buy=self.group2_buy3, userID=self.user3, percent=90000)

        self.url = '/auth/LeaveGroup/'

    def test_leave_user_from_group1_successfully(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(self.url, data={'groupID':self.group1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), {"message":"User deleted successfully."})
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).count(), 2)
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).first().userID, self.user1)
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).last().userID, self.user3)

    def test_leave_user_from_group2_successfully(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, data={'groupID':self.group2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), {"message":"User deleted successfully."})
        self.assertEqual(Members.objects.filter(groupID = self.group2.id).count(), 2)
        self.assertEqual(Members.objects.filter(groupID = self.group2.id).first().userID, self.user2)
        self.assertEqual(Members.objects.filter(groupID = self.group2.id).last().userID, self.user3)

    def test_leave_user_from_group_with_creditor(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, data={'groupID':self.group1.id})
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(json.loads(response.content), {"message":"The settlement has not been completed"})
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).count(), 3)
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).first().userID, self.user1)
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).last().userID, self.user3)
        self.assertTrue(Members.objects.get(groupID = self.group1.id, userID = self.user1))

    def test_leave_user_from_group_with_debtor(self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(self.url, data={'groupID':self.group1.id})
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(json.loads(response.content), {"message":"The settlement has not been completed"})
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).count(), 3)
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).first().userID, self.user1)
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).last().userID, self.user3)
        self.assertTrue(Members.objects.get(groupID = self.group1.id, userID = self.user1))

    def test_leave_group_user_not_found(self):
        self.client.force_authenticate(user=self.user4)
        response = self.client.post(self.url, data={'groupID':self.group2.id})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {"message":"User not found."})
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).count(), 3)
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).first().userID, self.user1)
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).last().userID, self.user3)
        self.assertTrue(Members.objects.get(groupID = self.group1.id, userID = self.user1))

    def test_leave_group_not_found(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(self.url, data={'groupID':10})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {"message":"Group not found."})
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).count(), 3)
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).first().userID, self.user1)
        self.assertEqual(Members.objects.filter(groupID = self.group1.id).last().userID, self.user3)
        self.assertTrue(Members.objects.get(groupID = self.group1.id, userID = self.user1))

    def test_leave_group_internal_server_error(self):
        # Mock the DebtandCreditforMemberinGroup function to raise an exception
        with patch('MyUser.views.DebtandCreditforMemberinGroup') as mock_function:
            mock_function.side_effect = Exception('Internal Server Error')
            self.client.force_authenticate(user=self.user1)
            response = self.client.post(self.url, data={'groupID': self.group1.id})
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(json.loads(response.content), {'message': 'Internal Server Error'})

    def test_post_without_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, data={'groupID': 1})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)