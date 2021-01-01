from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Label(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    label_name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.label_name

class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=500)
    date = models.DateTimeField(default = datetime.now())
    label = models.ForeignKey(Label, blank=True, null=True, on_delete=models.DO_NOTHING)
    is_archive = models.BooleanField(default=False)
    is_trash = models.BooleanField(default=False)
    last_updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date']

