from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.urls import reverse
from rest_framework import status
import json


class TestNotesAPIs(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_1 = User.objects.create_user(username='birajit95',email='birajit95@gmail.com',password='123456')
        self.user_2 = User.objects.create_user(username='aryan75',email='aryan95@gmail.com',password='123456')

        self.valid_payload_1 = {
            'title':'Hello',
            'content':'world',
            'label':[{
                'label_name':'Google'
            }],
            'color':'#FF5733'
        }

    def user_login(self, user=None):
        if user:
            username='birajit95'
        else:
            username = 'aryan75'
        self.valid_credential = json.dumps({
            'username':username,
            'password':'123456'
        })
        self.client.post(reverse('userLogin'), data=self.valid_credential, content_type='application/json')

    def test_add_label_when_user_is_logged_in(self, label_name='Google'):
        self.user_login(user='birajit95')
        label = json.dumps({
            'label_name':label_name
        })
        response = self.client.post(reverse('addLabel'), data=label, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data['response_msg'], 'Label added')

    def test_add_label_when_user_is_not_logged_in(self, label_name='Facebook'):
        label = json.dumps({
            'label_name':label_name
        })
        response = self.client.post(reverse('addLabel'), data=label, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(response.url, '/user/login/?next=/notes/add-label/')

    def test_add_label_when_user_is_logged_in_and_given_black_input(self, label_name=None):
        self.user_login(user='birajit95')
        label = json.dumps({
            'label_name':label_name
        })
        response = self.client.post(reverse('addLabel'), data=label, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_labels_when_user_is_loged_in_and_no_labels_found(self):
        self.user_login(user='birajit95')
        response = self.client.get(reverse('getLabels'))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data['response_data'],'No labels found')

    def test_get_all_labels_when_user_is_not_loged_in(self):
        response = self.client.get(reverse('getLabels'))
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(response.url,'/user/login/?next=/notes/get-labels/')

    def test_get_all_labels_when_user_is_loged_in_and_labels_found(self):
        self.user_login(user='birajit95')
        self.test_add_label_when_user_is_logged_in(label_name='Cat')
        self.test_add_label_when_user_is_logged_in(label_name='Dog')
        response = self.client.get(reverse('getLabels'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
