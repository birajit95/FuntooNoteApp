from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    dob = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_pics',default='default.jpg')

    def save(self):
        super(Profile, self).save()
        img = Image.open(self.image.path)
        if img.height > 300 and img.width > 300:
            img.thumbnail((300,300))
            img.save(self.image.path)



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class TokenBlackLists(models.Model):
    token = models.CharField(max_length=500)
    datetime = models.DateTimeField(default=datetime.now())