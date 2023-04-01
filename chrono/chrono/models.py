from django.db import models

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    profile_picture = models.CharField(max_length=1000, null=False, blank=False)
    interval = models.CharField(max_length=255, blank=False) # format 8,16


class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255, null=False, blank=False, unique=True)
    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    password = models.CharField(max_length=255, null=False, blank=False)
    comapny = models.ForeignKey(Company, on_delete=models.CASCADE)

class Application(models.Model):
    logo = models.CharField(max_length=1000, null=False, blank=False)
    name = models.CharField(max_length=255, blank=False)

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    timestamp = models.DateField()
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
