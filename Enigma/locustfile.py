from locust import HttpUser, task
import random

class ListPostUser(HttpUser):

    @task
    def show_member(self):
        # Authenticate first
        auth_response = self.client.post('auth/token/', json={"username": "a@a.com", "password": "1"})
        if auth_response.status_code != 200:
            print('Authentication failed')
            return
        
        token = auth_response.json().get('token')

        headers = {'Authorization': f'Token {token}'}
        
        data = {'groupID': random.randrange(10, 5000)}
        response = self.client.post('group/ShowMembers/', json=data, headers=headers)
        
        if response.status_code != 200:
            print(f'Request failed with status code: {response.text}')
    
    
    @task
    def UserInfo(self):
        # Authenticate first
        auth_response = self.client.post('auth/token/', json={"username": "a@a.com", "password": "1"})
        if auth_response.status_code != 200:
            print('Authentication failed')
            return

        token = auth_response.json().get('token')

        headers = {'Authorization': f'Token {token}'}

        response = self.client.post('auth/UserInfo/',  headers=headers)

        if response.status_code != 200:
            print(f'Request failed with status code: {response.status_code}')

    @task
    def Group_Info(self):
        # Authenticate first
        auth_response = self.client.post('auth/token/', json={"username": "a@a.com", "password": "1"})
        if auth_response.status_code != 200:
            print('Authentication failed')
            return

        token = auth_response.json().get('token')

        headers = {'Authorization': f'Token {token}'}

        data = {'groupID': random.randrange(10, 5000)}
        response = self.client.post('group/GroupInfo/', json=data, headers=headers)

        if response.status_code != 200:
            print(response)
            print(f'Request failed with status code: {response.status_code}')


