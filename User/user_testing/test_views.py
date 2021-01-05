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

    def test_user_email_validated_when_given_valid_token(self):
        response = self.client.post(reverse('userRegistration'), data=json.dumps(self.valid_payload), content_type='application/json')
        jwtTokn = response.data['response_data']
        get_respose = self.client.get("http://127.0.0.1:8000/user/verify-email/?token="+jwtTokn, content_type='application/json')
        self.assertEquals(get_respose.status_code, status.HTTP_200_OK)

    def test_user_email_validated_when_given_invalid_token(self):
        jwtTokn = """eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFrYXNoMTIzIiwicGFzc3dvcmQiOiJwYmtkZjJfc2hhMjU2JDE4MDAwMCRxdDBFa3Vxa2t4ZU8kNndURDMrWGF2SENyTGQwSHM3S3BmYlo1b01v
        NWIzTkZEZStDMTlBM0ZXdz0iLCJleHAiOjE2MDk5NTA2MT.l31v9OmEZoMFSHA4LycwsDT4oD-lxm5VUkEz3Zrn_28"""
        get_respose = self.client.get("http://127.0.0.1:8000/user/verify-email/?token="+jwtTokn, content_type='application/json')
        self.assertEquals(get_respose.status_code, status.HTTP_401_UNAUTHORIZED)
