from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from PIL import Image
from django.utils.timezone import now

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    dob = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_pics',default='profile_pics/default.jpg')

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 and img.width > 300:
            img.thumbnail((300,300))
            img.save(self.image.path)


class TokenBlackLists(models.Model):
    token = models.CharField(max_length=500)
    datetime = models.DateTimeField(default=now)