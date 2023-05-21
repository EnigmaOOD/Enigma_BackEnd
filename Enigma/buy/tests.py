from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from Group.models import Group, Members
from MyUser.models import MyUser
from unittest import mock
from buy.models import buy, buyer, consumer
import json


class UserGroupBuysTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = MyUser.objects.create(
            name='Nina', email='Nina@test.com', password='NinaPass')
        self.user2 = MyUser.objects.create(
            name='Minoo', email='Minoo@test.com', password='MinooPass')

        self.group = Group.objects.create(name='Group1')
        Members.objects.create(userID=self.user1, groupID=self.group)
        Members.objects.create(userID=self.user2, groupID=self.group)

        self.buy1 = buy.objects.create(
            description='Buy1', cost=200, groupID=self.group, added_by=self.user2)
        self.buy2 = buy.objects.create(
            description='Buy2', cost=100, groupID=self.group, added_by=self.user2)

        self.buyer1 = buyer.objects.create(
            buy=self.buy1, userID=self.user1, percent=200)
        self.buyer2 = buyer.objects.create(
            buy=self.buy2, userID=self.user2, percent=100)

        self.consumer1 = consumer.objects.create(
            buy=self.buy1, userID=self.user1, percent=170)
        self.consumer2 = consumer.objects.create(
            buy=self.buy1, userID=self.user2, percent=30)
        self.consumer3 = consumer.objects.create(
            buy=self.buy2, userID=self.user1, percent=100)

        self.url = '/buy/UserGroupBuys/'

    def test_UserGroupBuys_should_success(self):
        self.client.force_authenticate(user=self.user1)
        data = {'groupID': self.group.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['buyer_buys']), 1)
        self.assertEqual(len(response.data['consumer_buys']), 2)
        self.assertEqual(response.data['buyer_buys'][0]['id'], self.buy1.id)
        self.assertEqual(response.data['consumer_buys'][0]['id'], self.buy1.id)
        self.assertEqual(response.data['consumer_buys'][1]['id'], self.buy2.id)

    def test_UserGroupBuys_should_success_when_user_just_buyer(self):
        user3 = MyUser.objects.create(
            name='Sam', email='Sam@test.com', password='SamPass')
        Members.objects.create(userID=user3, groupID=self.group)

        buy3 = buy.objects.create(
            description='Buy3', cost=50, groupID=self.group, added_by=self.user2)
        buyer3 = buyer.objects.create(buy=buy3, userID=user3, percent=50)
        self.client.force_authenticate(user=user3)
        data = {'groupID': self.group.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['buyer_buys']), 1)
        self.assertEqual(len(response.data['consumer_buys']), 0)
        self.assertEqual(response.data['buyer_buys'][0]['id'], buy3.id)

    def test_UserGroupBuys_should_success_when_user_just_consumer(self):
        user4 = MyUser.objects.create(
            name='Masih', email='Masih@test.com', password='MasihPass')
        Members.objects.create(userID=user4, groupID=self.group)

        buy4 = buy.objects.create(
            description='Buy4', cost=20, groupID=self.group, added_by=self.user2)
        consumer4 = consumer.objects.create(buy=buy4, userID=user4, percent=20)
        self.client.force_authenticate(user=user4)
        data = {'groupID': self.group.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['buyer_buys']), 0)
        self.assertEqual(len(response.data['consumer_buys']), 1)
        self.assertEqual(response.data['consumer_buys'][0]['id'], buy4.id)

    def test_UserGroupBuys_should_success_with_sort(self):
        self.client.force_authenticate(user=self.user1)
        data = {'groupID': self.group.id, 'sort': 'cost'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['buyer_buys']), 1)
        self.assertEqual(len(response.data['consumer_buys']), 2)
        self.assertEqual(response.data['buyer_buys'][0]['id'], self.buy1.id)
        self.assertEqual(response.data['consumer_buys'][0]['id'], self.buy2.id)
        self.assertEqual(response.data['consumer_buys'][1]['id'], self.buy1.id)

    def test_UserGroupBuys_should_success_when_empty(self):
        group2 = Group.objects.create(name='Group2')
        user1 = MyUser.objects.create(
            email='user1@test.com', password='testpass', name='test')
        Members.objects.create(userID=user1, groupID=group2)
        data = {'groupID': group2.id}
        self.client.force_authenticate(user=user1)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['buyer_buys']), 0)
        self.assertEqual(len(response.data['consumer_buys']), 0)

    def test_UserGroupBuys_should_Error_when_invalid_groupID(self):
        self.client.force_authenticate(user=self.user1)
        data = {'groupID': 9999}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Group ID not provided')

    def test_UserGroupBuys_should_Error_when_missing_groupID(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_UserGroupBuys_should_Error_when_not_authenticated(self):
        data = {'groupID': self.group.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_UserGroupBuys_should_Error_when_user_not_member_of_group(self):
        user2 = MyUser.objects.create(
            email='user2@test.com', password='testpass', name='test')
        self.client.force_authenticate(user=user2)
        data = {'groupID': self.group.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('buy.views.buy.objects.filter')
    def test_UserGroupBuys_should_Error_when_server_error(self, mock_filter):
        mock_filter.side_effect = Exception('Test Exception')
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, {'groupID': self.group.id})
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['message'], 'An error occurred.')

    def test_UserGroupBuys_should_Error_with_get_method(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_UserGroupBuys_should_Error_with_put_method(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class GetGroupBuysTestCase(APITestCase):
    def setUp(self):
        self.user = MyUser.objects.create(
            email='testuser', password='testpass')
        self.group = Group.objects.create(name='Test Group')
        Members.objects.create(userID=self.user, groupID=self.group)

        self.buy1 = buy.objects.create(
            groupID=self.group, cost=10, added_by=self.user)
        self.buy2 = buy.objects.create(
            groupID=self.group, cost=20, added_by=self.user)
        self.buy3 = buy.objects.create(
            groupID=self.group, cost=5, added_by=self.user)
        self.url = '/buy/GetGroupBuys/'

    def test_GetGroupBuys_should_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'groupID': self.group.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['cost'], 10)
        self.assertEqual(response.data[1]['cost'], 20)
        self.assertEqual(response.data[2]['cost'], 5)

    def test_GetGroupBuys_should_success_with_sort(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {'groupID': self.group.id, 'sort': 'cost'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['cost'], 5)
        self.assertEqual(response.data[1]['cost'], 10)
        self.assertEqual(response.data[2]['cost'], 20)

    def test_GetGroupBuys_should_success_when_no_buys(self):
        group = Group.objects.create(name='Empty Group')
        self.client.force_authenticate(user=self.user)
        Members.objects.create(userID=self.user, groupID=group)
        response = self.client.post(self.url, {'groupID': group.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_GetGroupBuys_should_success_with_same_cost(self):
        group = Group.objects.create(name='Same Cost Group')
        buy1 = buy.objects.create(groupID=group, cost=10, added_by=self.user)
        buy2 = buy.objects.create(groupID=group, cost=10, added_by=self.user)
        self.client.force_authenticate(user=self.user)
        Members.objects.create(userID=self.user, groupID=group)
        response = self.client.post(self.url, {'groupID': group.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_GetGroupBuys_should_success_with_same_cost_sorted(self):
        group = Group.objects.create(name='Same Cost Group')
        buy1 = buy.objects.create(groupID=group, cost=10, added_by=self.user)
        buy2 = buy.objects.create(groupID=group, cost=10, added_by=self.user)
        self.client.force_authenticate(user=self.user)
        Members.objects.create(userID=self.user, groupID=group)
        response = self.client.post(
            self.url, {'groupID': group.id, 'sort': 'cost'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['cost'], 10)
        self.assertEqual(response.data[0]['id'], buy1.id)

    def test_GetGroupBuys_should_success_with_large_data_set(self):
        group = Group.objects.create(name='Large Group')
        for i in range(100):
            buy.objects.create(groupID=group, cost=i, added_by=self.user)
        self.client.force_authenticate(user=self.user)
        Members.objects.create(userID=self.user, groupID=group)
        response = self.client.post(self.url, {'groupID': group.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 100)
        self.assertEqual(response.data[0]['cost'], 0)
        self.assertEqual(response.data[99]['cost'], 99)

    def test_GetGroupBuys_should_Error_when_unauthenticated(self):
        response = self.client.post(self.url, {'groupID': self.group.id})
        # becuase of permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_GetGroupBuys_should_Error_when_invalid_groupID(self):
        self.client.force_authenticate(user=self.user)
        # 999 is an invalid group ID
        response = self.client.post(self.url, {'groupID': 999})
        # becuase of permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_GetGroupBuys_should_Error_when_missing_groupID(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)  # Missing groupID parameter
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_GetGroupBuys_should_Error_when_user_not_member_of_group(self):
        group = Group.objects.create(name='Test Group')
        buy.objects.create(groupID=group, cost=1, added_by=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'groupID': group.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('buy.views.buy.objects.filter')
    def test_GetGroupBuys_should_Error_when_server_error(self, mock_filter):
        mock_filter.side_effect = Exception('Test Exception')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'groupID': self.group.id})
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['message'], 'An error occurred.')

    def test_GetGroupBuys_should_Error_with_get_method(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_GetGroupBuys_should_Error_with_put_method(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



class CreateBuyViewTest(APITestCase):
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

        self.url = '/buy/CreateBuyView/'

    def test_CreateBuyView_should_Error_without_authentication(self):
        data = {
            "buyers": [
                {
                    "userID": 1,
                    "percent": 85000
                }
            ],
            "consumers": [
                {
                    "userID": 1,
                    "percent": 45000
                },
                {
                    "userID": 3,
                    "percent": 40000
                }
            ],
            "description": "Test Buy",
            "cost": 85000,
            "date": "2023-02-7",
            "picture_id": 1,
            "groupID": 1
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_CreateBuyView_should_success_with_valid_data(self):
        self.client.force_authenticate(user=self.user1)

        data = {
            "buyers": [
                {
                    "userID": 1,
                    "percent": 85000
                }
            ],
            "consumers": [
                {
                    "userID": 1,
                    "percent": 45000
                },
                {
                    "userID": 3,
                    "percent": 40000
                }
            ],
            "description": "Test Buy",
            "cost": 85000,
            "date": "2023-02-7",
            "picture_id": 1,
            "groupID": 1
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(buy.objects.count(), 1)

        buy1 = buy.objects.first()
        self.assertEqual(buy1.description, 'Test Buy')
        self.assertEqual(str(buy1.date), '2023-02-07')
        self.assertEqual(buy1.cost, 85000)
        self.assertEqual(buy1.picture_id, 1)
        self.assertEqual(buy1.groupID.id, 1)

        list_buyer = buyer.objects.filter(buy=buy1)
        self.assertEqual(list_buyer.count(), 1)
        self.assertEqual(list_buyer.first().userID, self.user1)
        self.assertEqual(list_buyer.first().percent, 85000)
        
        list_consumer = consumer.objects.filter(buy=buy1)
        self.assertEqual(list_consumer.count(), 2)
        self.assertEqual(list_consumer.first().userID, self.user1)
        self.assertEqual(list_consumer.first().percent, 45000)
        self.assertEqual(list_consumer.last().userID, self.user3)
        self.assertEqual(list_consumer.last().percent, 40000)

    def test_CreateBuyView_should_success_when_description_null(self):
        self.client.force_authenticate(user=self.user1)

        data = {
            "buyers": [
                {
                    "userID": 1,
                    "percent": 85000
                }
            ],
            "consumers": [
                {
                    "userID": 1,
                    "percent": 45000
                },
                {
                    "userID": 3,
                    "percent": 40000
                }
            ],
            "description": "",
            "cost": 85000,
            "date": "2023-02-7",
            "picture_id": 1,
            "groupID": 1
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(buy.objects.count(), 1)

        buy1 = buy.objects.first()
        self.assertEqual(buy1.description, '')
        self.assertEqual(str(buy1.date), '2023-02-07')
        self.assertEqual(buy1.cost, 85000)
        self.assertEqual(buy1.picture_id, 1)
        self.assertEqual(buy1.groupID.id, 1)

        list_buyer = buyer.objects.filter(buy=buy1)
        self.assertEqual(list_buyer.count(), 1)
        self.assertEqual(list_buyer.first().userID, self.user1)
        self.assertEqual(list_buyer.first().percent, 85000)
        
        list_consumer = consumer.objects.filter(buy=buy1)
        self.assertEqual(list_consumer.count(), 2)
        self.assertEqual(list_consumer.first().userID, self.user1)
        self.assertEqual(list_consumer.first().percent, 45000)
        self.assertEqual(list_consumer.last().userID, self.user3)
        self.assertEqual(list_consumer.last().percent, 40000)

    def test_CreateBuyView_should_success_when_no_cost(self):
        self.client.force_authenticate(user=self.user1)

        data = {
            "buyers": [
                {
                    "userID": 1,
                    "percent": 85000
                }
            ],
            "consumers": [
                {
                    "userID": 1,
                    "percent": 45000
                },
                {
                    "userID": 3,
                    "percent": 40000
                }
            ],
            "description": "",
            "date": "2023-02-7",
            "picture_id": 1,
            "groupID": 1
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(buy.objects.count(), 0)
        self.assertEqual(json.loads(response.content), {"cost":["This field is required."]})

    # def test_create_buy_with_valid_payload(self):
    #     self.client.force_authenticate(user=self.user1)
    #     response = self.client.post('/buy/CreateBuyView/', self.valid_payload)
    #     print(response.json())
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data['groupID'], self.valid_payload['groupID'])
    #     self.assertEqual(response.data['description'], self.valid_payload['description'])
    #     self.assertEqual(response.data['cost'], self.valid_payload['cost'])
    #     self.assertEqual(response.data['added_by'], self.valid_payload['added_by'])
    #     self.assertEqual(response.data['added_by'], self.valid_payload['added_by'])