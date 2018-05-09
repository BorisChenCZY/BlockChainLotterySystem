from django.db import models
from django.contrib import admin

class Artivle(models.Model):
    title = models.CharField(max_length=32,default='title')
    content = models.TextField(null=True)
    pub_time = models.DateTimeField(null=True)

    def __str__(self):
        return self.title

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)



admin.site.register(User)