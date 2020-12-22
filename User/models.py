from django.db import models
from datetime import datetime


class User(models.Model):
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    userName = models.CharField(max_length=30)
    email = models.CharField(max_length=40)
    password = models.CharField(max_length=100)
    date = models.DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return f"{self.firstName} {self.lastName}"
