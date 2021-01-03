from django.urls import reverse, resolve
from django.test import SimpleTestCase
from ..views import UserRegistration, VerifyEmail, UserLogin, UserLogOut, ForgotPassword,\
    ResetPassword, UserProfile, UpdateProfilePictureAPI, ChangePassword

class TestUrls(SimpleTestCase):
    def test_registration_url_is_resolved(self):
        url = reverse('userRegistration')
        self.assertEquals(resolve(url).func.view_class, UserRegistration)

    def test_verify_email_url_is_resolved(self):
        url = reverse('verifyEmail')
        self.assertEquals(resolve(url).func.view_class, VerifyEmail)

    def test_user_login_url_is_resolved(self):
        url = reverse('userLogin')
        self.assertEquals(resolve(url).func.view_class, UserLogin)

    def test_user_logout_url_is_resolved(self):
        url = reverse('userLogout')
        self.assertEquals(resolve(url).func.view_class, UserLogOut)

    def test_forgot_password_url_is_resolved(self):
        url = reverse('forgotPassword')
        self.assertEquals(resolve(url).func.view_class, ForgotPassword)

    def test_reset_password_url_is_resolved(self):
        url = reverse('resetPassword',args=['uid','token'])
        self.assertEquals(resolve(url).func.view_class, ResetPassword)

    def test_change_password_url_is_resolved(self):
        url = reverse('changePassword')
        self.assertEquals(resolve(url).func.view_class, ChangePassword)

    def test_user_profile_url_is_resolved(self):
        url = reverse('userProfile')
        self.assertEquals(resolve(url).func.view_class, UserProfile)

    def test_update_profile_picture_url_is_resolved(self):
        url = reverse('userProfilePic')
        self.assertEquals(resolve(url).func.view_class, UpdateProfilePictureAPI)