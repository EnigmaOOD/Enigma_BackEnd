import json
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest import mock
from unittest.mock import patch
from Group.models import Group, Members
from Group.views import DebtandCreditforMemberinGroup
from Group.serializers import GroupSerializer
from MyUser.models import MyUser
from buy.models import buy, buyer, consumer


class DeleteGroupTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = MyUser.objects.create(
            email='testuser@test.local', password='testpass',  name='test', picture_id=4)
        self.group = Group.objects.create(name='Test Group')
        Members.objects.create(userID=self.user, groupID=self.group)
        self.url = "/group/DeleteGroup/"

    def test_DeleteGroup_should_success(self):
        self.client.force_authenticate(user=self.user)
        data = {'groupID': self.group.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {'message': 'Group deleted successfully.'})

    def test_DeleteGroup_should_Error_when_group_not_exist(self):
        self.client.force_authenticate(user=self.user)
        data = {'groupID': 9999}  # invalid group ID
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code,
                         status.HTTP_403_FORBIDDEN)  # permission
        self.assertTrue(Group.objects.filter(id=self.group.id).exists())

    def test_DeleteGroup_should_Error_when_user_not_member_of_group(self):
        user2 = MyUser.objects.create(
            email='user2@test.com', password='testpass', name='test')
        self.client.force_authenticate(user=user2)
        data = {'groupID': self.group.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_DeleteGroup_should_Error_with_exception(self):
        self.client.force_authenticate(user=self.user)
        data = {'groupID': self.group.id}
        with mock.patch('Group.models.Group.objects.get') as mock_get:
            mock_get.side_effect = Exception('Something went wrong')
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def test_DeleteGroup_should_Error_without_authenticated(self):
        data = {'groupID': self.group.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_DeleteGroup_should_Error_with_put_method(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_DeleteGroup_should_Error_with_get_method(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class DebtandCreditforMemberinGroupTest(APITestCase):
    def setUp(self):
        self.user1 = MyUser.objects.create(email='test1@example.com', name='test1', password='test1')
        self.user2 = MyUser.objects.create(email='test2@example.com', name='test2', password='test2')

        self.group = Group.objects.create(name='Test Group', currency='تومان')

        self.group1_member1 = Members.objects.create(userID = self.user1, groupID=self.group)
        self.group1_member2 = Members.objects.create(userID = self.user2, groupID=self.group)

        self.buy = buy.objects.create(groupID= self.group, cost=85000, date= "2023-02-01", picture_id= 1, added_by=self.user1)
        self.buyer = buyer.objects.create(buy=self.buy, userID=self.user1, percent=85000)
        self.consumer1 = consumer.objects.create(buy=self.buy, userID=self.user1, percent=45000)
        self.consumer2 = consumer.objects.create(buy=self.buy, userID=self.user2, percent=40000)

    def test_DebtandCreditforMemberinGroupTest_should_success_with_debt(self):
        result = DebtandCreditforMemberinGroup(self.user1.pk, self.group.pk)
        self.assertEqual(result, 40000)

    def test_DebtandCreditforMemberinGroupTest_should_success_with_credit(self):
        result = DebtandCreditforMemberinGroup(self.user2.pk, self.group.pk)
        self.assertEqual(result, -40000)

    def test_DebtandCreditforMemberinGroupTest_should_Error_when_group_not_found(self):
        result = DebtandCreditforMemberinGroup(self.user1.pk, 999)
        self.assertEqual(result, 'Group not found.')

    def test_DebtandCreditforMemberinGroupTest_should_Error_when_user_not_found(self):
        result = DebtandCreditforMemberinGroup(999, self.group.pk)
        self.assertEqual(result, 'User not found.')
    
    def test_DebtandCreditforMemberinGroupTest_should_Error_when_get_Exception(self):
        with self.assertRaises(Exception) as e:
            raise Exception('Your expected error message')
        self.assertEqual(str(e.exception), 'Your expected error message')

class GroupInfoTest(APITestCase):
    def setUp(self):
        self.user1 = MyUser.objects.create(
            email='maryam@test.local', name='maryam', password='maryam', picture_id=2)
        self.client = APIClient()
        self.group = Group.objects.create(
            name='Test Group', description="Family", currency="تومان", picture_id=2)
        Members.objects.create(userID=self.user1, groupID=self.group)
        self.valid_payload = {'groupID': self.group.id}
        self.invalid_payload = {'groupID': 999}
        self.url = '/group/GroupInfo/'

    def test_GroupInfo_should_success_with_valid_GroupID(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = GroupSerializer(self.group)
        self.assertEqual(response.data, serializer.data)

    def test_GroupInfo_should_Error_with_invalid_GroupID(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'message': 'Group not found.'})

    def test_GroupInfo_should_Error_without_authentication(self):
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_GroupInfo_should_Error_with_exception(self):
        self.client.force_authenticate(user=self.user1)
        with mock.patch('Group.models.Group.objects.get') as mock_get:
            mock_get.side_effect = Exception('Something went wrong')
            response = self.client.post(self.url, self.valid_payload)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_GroupInfo_should_Error_without_groupID(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'message': 'Group not found.'})

    def test_GroupInfo_should_Error_when_user_not_member_of_group(self):
        user2 = MyUser.objects.create(
            email='user2@test.com', password='testpass', name='test')
        self.client.force_authenticate(user=user2)
        data = {'groupID': self.group.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_GroupInfo_should_Error_when_invalid_dataType_groupID(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, {'groupID': 'invalid'})
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_GroupInfo_should_Error_with_put_method(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_GroupInfo_should_Error_with_get_method(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

class ShowGroupsTestCase(APITestCase):
    def setUp(self):
        self.user = MyUser.objects.create(
            email='testuser@test.local', password='testpass',  name='test', picture_id=4)
        self.url = '/group/ShowGroups/'

    def test_ShowGroups_should_success(self):
        self.client.force_authenticate(user=self.user)
        group = Group.objects.create(name='Test Group', currency='USD')
        Members.objects.create(userID=self.user, groupID=group)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['groups'], [
                         {'id': group.id, 'name': group.name, 'currency': group.currency}])

    def test_ShowGroups_should_success_for_multiple_groups(self):
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

    def test_ShowGroups_should_Error_when_no_groups(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data, {'Error': 'User does not belong to any groups'})

    def test_ShowGroups_should_Error_when_unauthenticated(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ShowGroups_should_Error_with_exception(self):
        self.client.force_authenticate(user=self.user)
        with mock.patch('Group.views.Members.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception('test exception')
            response = self.client.post(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, {'Error': 'test exception'})

    def test_ShowGroups_should_Error_with_empty_DB(self):
        self.client.force_authenticate(user=self.user)
        Members.objects.all().delete()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Error', response.data)

    def test_ShowGroups_should_Error_when_put_method(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_ShowGroups_should_Error_when_get_method(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class ShowMembersTests(APITestCase):
    def setUp(self):
        self.group = Group.objects.create(name='Test Group', currency='USD')
        self.user1 = MyUser.objects.create(
            email='test1@test.com', password='testpass')
        self.user2 = MyUser.objects.create(
            email='test2@test.com', password='testpass')
        self.user3 = MyUser.objects.create(
            email='test3@test.com', password='testpass')

        Members.objects.create(userID=self.user1, groupID=self.group)
        Members.objects.create(userID=self.user2, groupID=self.group)

        self.url = '/group/ShowMembers/'

    def test_ShowMembers_should_success(self):
        self.client.force_authenticate(user=self.user1)
        data = {'groupID': self.group.id}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_ShowMembers_should_success_when_valid_groupID(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, data={'groupID': self.group.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['userID']
                         ['user_id'], self.user1.user_id)
        self.assertEqual(response.data[1]['userID']
                         ['user_id'], self.user2.user_id)
        self.assertEqual(response.data[0]['userID']['email'], self.user1.email)
        self.assertEqual(response.data[1]['userID']['email'], self.user2.email)

    def test_ShowMembers_should_Error_when_invalid_groupID(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, {'groupID': self.group.id+1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ShowMembers_should_Error_when_wrong_user(self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(self.url, {'groupID': self.group.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ShowMembers_should_Error_when_no_members(self):
        self.client.force_authenticate(user=self.user1)
        group = Group.objects.create(name='Empty Group', currency='USD')
        response = self.client.post(self.url, {'groupID': group.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ShowMembers_should_Error_with_exception(self):
        self.client.force_authenticate(user=self.user1)
        with mock.patch('Group.views.DebtandCreditforMemberinGroup', side_effect=Exception('Test Exception')):
            response = self.client.post(self.url, {'groupID': self.group.id})
            self.assertEqual(response.status_code,
                             status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data, {'Error': 'Test Exception'})

    def test_ShowMembers_should_Error_with_put_method(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ShowMembers_should_Error_with_get_method(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CreateGroupTest(APITestCase):
    def setUp(self):
        self.user1 = MyUser.objects.create(
            email='test1@example.com', password='test1', name='test1', picture_id=1)
        self.user2 = MyUser.objects.create(
            email='test2@example.com', password='test2', name='test2', picture_id=2)
        self.user3 = MyUser.objects.create(
            email='test3@example.com', password='test3', name='test3', picture_id=3)

    def test_CreateGroup_should_success_with_valid_data(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 1,
            'emails': ["test2@example.com", "test3@example.com"]
        }
        response = self.client.post(
            '/group/CreateGroup/', data=data, format='json')

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

    def test_CreateGroup_should_Error_without_authentication(self):
        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 1,
            'emails': ["test2@example.com", "test3@example.com"]
        }
        response = self.client.post('/group/CreateGroup/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_CreateGroup_should_Error_when_name_empty(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        data = {
            'name': '',
            'currency': 'تومان',
            'picture_id': 1,
            'emails': ["test2@example.com", "test3@example.com"]
        }
        response = self.client.post(
            '/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {
                         "name": ["This field may not be blank."]})
        self.assertEqual(Group.objects.count(), 0)

    def test_CreateGroup_should_Error_when_name_space(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        data = {
            'name': '         ',
            'currency': 'تومان',
            'picture_id': 1,
            'emails': ["test2@example.com", "test3@example.com"]
        }
        response = self.client.post(
            '/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {
                         "name": ["This field may not be blank."]})
        self.assertEqual(Group.objects.count(), 0)

    def test_CreateGroup_should_success_when_description_null(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 1,
            'emails': ["test2@example.com", "test3@example.com"]
        }
        response = self.client.post(
            '/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 1)

    def test_CreateGroup_should_Error_when_currency_null(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        data = {
            'name': 'Test Group',
            'currency': '',
            'picture_id': 1,
            'emails': ["test2@example.com", "test3@example.com"]
        }
        response = self.client.post(
            '/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {
                         "currency": ["This field may not be blank."]})
        self.assertEqual(Group.objects.count(), 0)

    def test_CreateGroup_should_success_when_pictureID_null(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user2)

        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'emails': ["test1@example.com", "test3@example.com"]
        }
        response = self.client.post(
            '/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 1)

    def test_CreateGroup_should_Error_when_pictureID_nagative(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user2)

        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': -1,
            'emails': ["test1@example.com", "test3@example.com"]
        }
        response = self.client.post(
            '/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"picture_id": [
                         "Ensure this value is greater than or equal to 0."]})
        self.assertEqual(Group.objects.count(), 0)

    def test_CreateGroup_should_Error_when_pictureID_more_than_values(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 4,
            'emails': ["test2@example.com", "test3@example.com"]
        }
        response = self.client.post(
            '/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"picture_id": [
                         "Ensure this value is less than or equal to 3."]})
        self.assertEqual(Group.objects.count(), 0)

    def test_CreateGroup_should_succes_with_no_email(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user2)

        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 3,
        }
        response = self.client.post(
            '/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 1)

        members = Members.objects.filter(groupID=Group.objects.first())
        self.assertEqual(members.count(), 1)
        self.assertEqual(members.first().userID, self.user2)

    def test_CreateGroup_should_succes_with_empty_email(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user2)

        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 3,
            'emails': []
        }
        response = self.client.post(
            '/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 1)

        members = Members.objects.filter(groupID=Group.objects.first())
        self.assertEqual(members.count(), 1)
        self.assertEqual(members.first().userID, self.user2)

    def test_CreateGroup_should_Error_when_valid_email_but_not_register(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user2)

        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 3,
            "emails": ["test3@example.com", "miss_ramazani@yahoo.com", "nourieh110@gmail"]
        }
        response = self.client.post(
            '/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {
                         "message": "user not found."})
        self.assertEqual(Group.objects.count(), 0)

    def test_CreateGroup_should_Error_when_invalid_email(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user2)

        data = {
            'name': 'Test Group',
            'currency': 'تومان',
            'picture_id': 3,
            "emails": ["test3@example.com", "miss_ramazani", "nourieh110gmail"]
        }
        response = self.client.post(
            '/group/CreateGroup/', data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {
                         "message": "user not found."})
        self.assertEqual(Group.objects.count(), 0)

    def test_CreateGroup_should_Error_with_put_method(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user2)

        response = self.client.put( '/group/CreateGroup/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_CreateGroup_should_Error_with_get_method(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user2)

        response = self.client.get( '/group/CreateGroup/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

class AddUserGroupTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = MyUser.objects.create(
            email='test1@example.com', name='test1', password='test1')
        self.user2 = MyUser.objects.create(
            email='test2@example.com', name='test2', password='test2')
        self.user3 = MyUser.objects.create(
            email='test3@example.com', name='test3', password='test3')
        self.url = '/group/AddUserGroup/'
        self.group = Group.objects.create(name='Test Group', currency='تومان')

    def test_AddUserGroup_should_success_with_valid_data(self):
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

    def test_AddUserGroup_should_Error_with_invalid_groupID(self):
        self.client.force_authenticate(user=self.user1)
        Members.objects.create(userID=self.user1, groupID=self.group)
        data = {
            "groupID": 999,
            "emails": ["test2@example.com", "test3@example.com"]
        }
        response = self.client.post(self.url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Members.objects.count(), 1)
        self.assertEqual(Members.objects.first().userID, self.user1)



    def test_AddUserGroup_should_Error_with_not_exits_groupID(self):
        self.client.force_authenticate(user=self.user1)
        Members.objects.create(userID=self.user1, groupID=self.group)
        data = {
            "groupID": 1000000,
            "emails": ["test2@example.com", "test3@example.com"]
        }
        response = self.client.post(self.url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Members.objects.count(), 1)
        self.assertEqual(Members.objects.first().userID, self.user1)


    def test_AddUserGroup_should_success_with_no_email(self):
        self.client.force_authenticate(user=self.user2)
        Members.objects.create(userID=self.user2, groupID=self.group)
        data = {
            "groupID": self.group.id,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Members.objects.count(), 1)

    def test_AddUserGroup_should_Error_with_invalid_email(self):
        self.client.force_authenticate(user=self.user1)
        Members.objects.create(userID=self.user1, groupID=self.group)
        data = {
            "groupID": self.group.id,
            "emails": ["test2@example.com", "test3.example.com", "test3@example.com"]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {
                         "message": "user not found."})
        self.assertEqual(Members.objects.count(), 2)
        self.assertEqual(Members.objects.first().userID, self.user1)
        self.assertEqual(Members.objects.last().userID, self.user2)

    def test_AddUserGroup_should_Error_with_valid_email_but_not_register(self):
        self.client.force_authenticate(user=self.user3)
        Members.objects.create(userID=self.user3, groupID=self.group)
        data = {
            'groupID': self.group.id,
            "emails": ["test1@example.com", "miss_ramazani@yahoo.com", "test2@example.com"]
        }
        response = self.client.post(self.url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {
                         "message": "user not found."})
        self.assertEqual(Members.objects.count(), 2)

    def test_AddUserGroup_should_success_with_valid_email_but_duplicate(self):
        self.client.force_authenticate(user=self.user1)
        Members.objects.create(userID=self.user1, groupID=self.group)
        data = {
            'groupID': self.group.id,
            "emails": ["test1@example.com"]
        }
        response = self.client.post(self.url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Members.objects.count(), 1)

    def test_AddUserGroup_should_Error_with_invalid_user(self):
        self.client.force_authenticate(user=self.user2)
        Members.objects.create(userID=self.user1, groupID=self.group)
        data = {
            'groupID': self.group.id,
            "emails": ["test1@example.com", "miss_ramazani@yahoo.com", "test2@example.com"]
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_AddUserGroup_should_Error_with_non_data(self):
        self.client.force_authenticate(user=self.user2)
        Members.objects.create(userID=self.user2, groupID=self.group)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content), {"message": "You do not have permission to perform this action."})
    
    def test_AddUserGroup_without_authentication(self):
        data = {
            'groupID': self.group.id,
            'emails': ['test1@example.com']
        }

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Members.objects.count(), 0)
        self.assertEqual(json.loads(response.content), {"message": "You do not have permission to perform this action."})
    
    def test_AddUserGroup_should_Error_with_put_method(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_AddUserGroup_should_Error_with_get_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
