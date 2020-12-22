from django.db import models
from datetime import datetime


class User(models.Model):
    firstName = models.CharField(30)
    lastName = models.CharField(30)
    userName = models.CharField(30)
    email = models.CharField(40)
    password = models.CharField(100)
    date = models.DateTimeField(default=datetime.utcnow())

    def __str__(self):
        return f"{self.firstName} {self.lastName}"
