from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
import json

class TestUserAPP(TestCase):
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

        self.valid_credential = {
            'username': 'akash123',
            'password': 'birajit123@'
        }
        self.invalid_credential = {
            'username': 'akash123',
            'password': 'birajit125'
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

    def test_user_login_when_given_valid_credential(self):
        self.test_user_email_validated_when_given_valid_token()
        response = self.client.post(reverse('userLogin'), data=json.dumps(self.valid_credential), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)

    def test_user_login_when_given_invalid_credential(self):
        self.test_user_email_validated_when_given_valid_token()
        response = self.client.post(reverse('userLogin'), data=json.dumps(self.invalid_credential), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_when_given_valid_credential_but_account_is_not_activated(self):
        self.test_user_registration_when_given_valid_payload()
        response = self.client.post(reverse('userLogin'), data=json.dumps(self.valid_credential), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_100_CONTINUE)

    def test_user_logout_when_user_is_not_logged_in(self):
        response = self.client.get(reverse('userLogout'))
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(response.url, '/user/login?next=/user/logout/')

    def test_user_logout_when_user_is_logged_in(self):
        self.test_user_login_when_given_valid_credential()
        response = self.client.get(reverse('userLogout'))
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(response.data['response_msg'], 'You are logged out successfully')

    def test_forgot_password_api_when_mail_id_is_registered(self):
        self.test_user_registration_when_given_valid_payload()
        email = json.dumps({'email':'birajitdemo@gmail.com'})
        response = self.client.post(reverse('forgotPassword'),data=email, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_100_CONTINUE)
        self.assertEquals(response.data['response_msg'], 'Password reset link is sent to your mail.')

    def test_forgot_password_api_when_mail_id_is_not_registered(self):
        email = json.dumps({'email':'birajit@gmail.com'})
        response = self.client.post(reverse('forgotPassword'),data=email, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data['response_msg'], 'Your Mail id is not registered')

    def test_forgot_password_api_when_mail_id_is_invalid(self):
        email = json.dumps({'email':'birajit1123.com'})
        response = self.client.post(reverse('forgotPassword'),data=email, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_api_when_given_valid_uid_and_valid_token(self):
        self.test_user_registration_when_given_valid_payload()
        email = json.dumps({'email': 'birajitdemo@gmail.com'})
        response1 = self.client.post(reverse('forgotPassword'), data=email, content_type='application/json')
        token = response1.data['response_data']
        uid = 1
        data = json.dumps({
            'password':'12345678',
            'confirm_password':'12345678'
        })
        response = self.client.put(reverse('resetPassword',args=[uid,token]),data=data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['response_msg'], 'Your password is reset successfully !')

    def test_reset_password_api_when_given_mismatch_passwords(self):
        self.test_user_registration_when_given_valid_payload()
        email = json.dumps({'email': 'birajitdemo@gmail.com'})
        response1 = self.client.post(reverse('forgotPassword'), data=email, content_type='application/json')
        token = response1.data['response_data']
        uid = 1
        data = json.dumps({
            'password':'12345678',
            'confirm_password':'abcdgdj'
        })
        response = self.client.put(reverse('resetPassword',args=[uid,token]),data=data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_api_when_given_invalid_token(self):
        self.test_user_registration_when_given_valid_payload()
        email = json.dumps({'email': 'birajitdemo@gmail.com'})
        response1 = self.client.post(reverse('forgotPassword'), data=email, content_type='application/json')
        token = response1.data['response_data']+'invalid'
        uid = 1
        data = json.dumps({
            'password':'12345678',
            'confirm_password':'12345678'
        })
        response = self.client.put(reverse('resetPassword',args=[uid,token]),data=data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)