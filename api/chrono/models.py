from django.db import models


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    profile_picture = models.CharField(max_length=1000, null=False, blank=False)
    interval = models.CharField(max_length=255, blank=False)  # format 8,16


class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255, null=False, blank=False, unique=True)
    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    password = models.CharField(max_length=255, null=False, blank=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)


class Application(models.Model):
    id = models.AutoField(primary_key=True)
    logo = models.CharField(max_length=1000, null=False, blank=False)
    name = models.CharField(max_length=255, blank=False)
    category = models.CharField(max_length=255, blank=False)
    score = models.IntegerField()

class Activity(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    timestamp = models.CharField(max_length=255, blank=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    duration = models.BigIntegerField()

class Badge(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    timestamp = models.CharField(max_length=255, blank=False)
    image = models.CharField(max_length=1000, null=False, blank=False)
