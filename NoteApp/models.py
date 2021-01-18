from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from colorful.fields import RGBColorField
from django.contrib.postgres.fields import JSONField

class Label(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    label_name = models.CharField(max_length=20, unique=False)

    def __str__(self):
        return self.label_name

class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=500)
    date = models.DateTimeField(default = datetime.now())
    label = models.ManyToManyField(to=Label)
    is_archive = models.BooleanField(default=False)
    is_trash = models.BooleanField(default=False)
    last_updated = models.DateTimeField(null=True, blank=True)
    color = RGBColorField(colors=['#FF0000', '#00FF00', '#0000FF'], null=True, blank=True)
    collaborators = JSONField(null=True, blank=True)
    trashed_time = models.DateTimeField(default=None, blank=True, null=True)
    reminder = models.DateTimeField(default=None, blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title}   ({self.pk})"

class ReminderNotes(Notes):
    class Meta:
        proxy = True
        ordering = ('reminder',)