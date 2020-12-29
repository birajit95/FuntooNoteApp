from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=500)
    date = models.DateTimeField(default = datetime.now())
    label = models.CharField(max_length=20, blank=True, null=True)
    is_archive = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

