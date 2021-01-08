from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..models import Label
from django.contrib.auth import login
from django.urls import reverse
from rest_framework import status
import json


class TestNotesAPIs(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_1 = User.objects.create_user(username='birajit95',email='birajit95@gmail.com',password='123456')
        self.user_2 = User.objects.create_user(username='aryan75',email='aryan95@gmail.com',password='123456')


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


    def userWiseLabelData(self, user_1_label=None, user_2_label=None):
        Label.objects.create(user=self.user_1, label_name=user_1_label)
        Label.objects.create(user=self.user_2, label_name=user_2_label)

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

    def test_delete_label_when_user_is_logged_in_and_label_is_found(self):
        self.test_add_label_when_user_is_logged_in(label_name="Cat")
        label_name = 'Cat'
        response = self.client.delete(reverse('deleteLabel',args=[label_name]))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['response_msg'],'Label deleted')

    def test_delete_label_when_user_is_logged_in_and_label_is_not_found(self):
        self.test_add_label_when_user_is_logged_in(label_name="Cat")
        label_name = 'Dog'
        response = self.client.delete(reverse('deleteLabel',args=[label_name]))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data['response_msg'],f'{label_name} label is not exist')

    def test_delete_labels_when_user_is_not_loged_in(self):
        label_name = "Google"
        response = self.client.delete(reverse('deleteLabel', args=[label_name]))
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(response.url,'/user/login/?next=/notes/delete-label/Google/')

    def test_delete_label_when_user_1_is_logged_in_and_tries_to_delete_user_2s_label(self):
        self.userWiseLabelData(user_1_label="Cat",user_2_label='Dog')
        self.user_login(user="birajit95")
        label_name = 'Dog'
        response = self.client.delete(reverse('deleteLabel',args=[label_name]))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data['response_msg'],f'{label_name} label is not exist')

    def test_add_note_with_label_and_color_when_user_is_logged_in(self):
        self.test_add_label_when_user_is_logged_in(label_name="Google")
        valid_payload_1 = {
            'title': 'Hello',
            'content': 'world',
            'label': [{
                'label_name': 'Google'
            }],
            'color': '#FF5733'
        }
        response = self.client.post(reverse('addNote'),data=json.dumps(valid_payload_1), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_add_note_without_label_and_color_when_user_is_logged_in(self):
        self.user_login()
        valid_payload_1 = {
            'title': 'Hello',
            'content': 'world',
        }
        response = self.client.post(reverse('addNote'),data=json.dumps(valid_payload_1), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_add_note_without_label_but_with_color_when_user_is_logged_in(self):
        self.user_login()
        valid_payload_1 = {
            'title': 'Hello',
            'content': 'world',
            'color': '#FF5733'
        }
        response = self.client.post(reverse('addNote'),data=json.dumps(valid_payload_1), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_add_note_with_label_but_without_color_when_user_is_logged_in(self):
        self.test_add_label_when_user_is_logged_in(label_name="Google")
        valid_payload_1 = {
            'title': 'Hello',
            'content': 'world',
            'label': [{
                'label_name': 'Google'
            }],
        }
        response = self.client.post(reverse('addNote'),data=json.dumps(valid_payload_1), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_add_note_with_label_but_label_is_not_present_and_when_user_is_logged_in(self):
        self.userWiseLabelData(user_1_label="Google",user_2_label="Cat")
        self.user_login(user='birajit95')
        valid_payload_1 = {
            'title': 'Hello',
            'content': 'world',
            'label': [{
                'label_name': 'Cat'
            }],
        }
        response = self.client.post(reverse('addNote'),data=json.dumps(valid_payload_1), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(f"{response.data['response_msg']}",'Cat label is not exist')