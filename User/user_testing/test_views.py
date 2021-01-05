from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
import json

class TestUserRegistration(TestCase):
    def setUp(self):
        self.client = Client()
        self.valid_payload = {
            'username':'akash123',
            'email': 'birajitdemo@gmail.com',
            'first_name':'Akash',
            'last_name':'Kumar',
            'password':'birajit123@'
        }

        self.invalid_payload = {
            'username': '',
            'email': 'birajitdemo@gmail.com',
            'first_name': 'Akash',
            'last_name': 'Kumar',
            'password': 'birajit123@'
        }

    def test_user_registration_when_given_valid_payload(self):
        response = self.client.post(reverse('userRegistration'),data=json.dumps(self.valid_payload),
                                     content_type = 'application/json'
                               )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_user_registration_when_given_invalid_payload(self):
        response = self.client.post(reverse('userRegistration'),data=json.dumps(self.invalid_payload),
                                     content_type = 'application/json'
                               )
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
