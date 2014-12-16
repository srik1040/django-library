from django.db import models
from django.contrib.auth.models import User
import hashlib

# Create your models here.

class Book(models.Model):
   title = models.CharField(max_length=200)
   ISBN = models.CharField(max_length=200)
   publisher = models.ForeignKey('Publisher')
   author = models.ForeignKey('Author')
   lend_period = models.ForeignKey('LendPeriods')
   page_amount = models.IntegerField()
   lend_by = models.ForeignKey('UserProfile')
   lend_from = models.DateField()

class LendPeriods(models.Model):
    name = models.CharField(max_length=50)
    days_amount = models.IntegerField()

class Publisher(models.Model):
    name = models.CharField(max_length=100)

class Author(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    date_of_birth = models.DateField()

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    mobile = models.CharField(max_length=15)
    website = models.CharField(max_length=50)
    fb_name = models.CharField(max_length=60)
    friends = models.ManyToManyField('self', symmetrical=True)
    join_date = models.DateField()

    def gravator_url(self):
        return "http://www.gravatar.com/avatar/%s?s=50" % hashlib.md5(self.user.email).hexdigest()

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])