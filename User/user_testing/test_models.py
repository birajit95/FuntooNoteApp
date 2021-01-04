from django.test import TestCase
from ..models import User

class TestUser(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='aryan95', email='aryan@gmail.com', first_name='Aryan',
                            last_name="Debnath", is_active=False)
        self.user.profile.bio = "I am a passionate software developer"
        self.user.profile.save()


    def test_user_first_name(self):
        user = User.objects.get(username='aryan95')
        self.assertEqual(user.first_name,'Aryan')

    def test_user_last_name(self):
        user = User.objects.get(username='aryan95')
        self.assertEqual(user.last_name, 'Debnath')

    def test_user_email(self):
        user = User.objects.get(username='aryan95')
        self.assertEqual(user.email, 'aryan@gmail.com')

    def test_user_bio(self):
        user = User.objects.get(username='aryan95')
        self.assertEqual(user.profile.bio, 'I am a passionate software developer')

    def test_user_profile_picture(self):
        user = User.objects.get(username='aryan95')
        self.assertEqual(user.profile.image, 'profile_pics/default.jpg')