from django.db import models
from django.contrib.auth.models import User
import hashlib
from django.utils import timezone


class Book(models.Model):
    """
    An Book class - to describe book in the system.
    """
    title = models.CharField(max_length=200)
    ISBN = models.CharField(max_length=200)
    publisher = models.ForeignKey('Publisher')
    author = models.ForeignKey('Author')
    lend_period = models.ForeignKey('LendPeriods')
    page_amount = models.IntegerField()
    lend_by = models.ForeignKey('UserProfile', null=True, blank=True)
    lend_from = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return 'Book: ' + self.title

    class Meta:
        ordering = ['title']
        verbose_name = "Book"
        verbose_name_plural = "Books"


class LendPeriods(models.Model):
    """
    Users can borrow books from library for different
    time period. This class defines frequently-used
    lending periods.
    """
    name = models.CharField(max_length=50)
    days_amount = models.IntegerField()

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        get_latest_by = "days_amount"
        ordering = ['days_amount']
        verbose_name = "Lending period"
        verbose_name_plural = "Lending periods"


class Publisher(models.Model):
    """
    Class defines book's publisher
    """
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return 'Publisher: %s' % self.name

    class Meta:
        get_latest_by = "name"
        ordering = ['name']
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"


class Author(models.Model):
    """
    Class defines book's author
    """
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    date_of_birth = models.DateField()

    def __unicode__(self):
        return 'Author: ' + self.name + ' ' + self.surname

    def __str__(self):
        return 'Author: ' + self.name + ' ' + self.surname

    class Meta:
        get_latest_by = "name"
        ordering = ['name', 'surname']
        verbose_name = "Author"
        verbose_name_plural = "Authors"


class QuotationFromBook(models.Model):
    """
    Class descirbes specific quotation from the book
    saved by specific user
    """
    user = models.ForeignKey(User, blank=False, null=False)
    book = models.ForeignKey(Book, blank=False, null=False)
    quotation = models.CharField(max_length=600, null=False, blank=False)
    creation_date = models.DateField(blank=False, null=False)

    def __unicode__(self):
        return 'quotation: %s...' % self.quotation[0:12]

    def get_full_quotation(self):
        return '%s' % self.quotation

    class Meta:
        get_latest_by = "creation_date"
        ordering = ['quotation']
        verbose_name = "Quotation"
        verbose_name_plural = "Quotations"


class UserProfile(models.Model):
    """
    Class provides more information according the system's users
    """
    user = models.OneToOneField(User)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    website = models.CharField(max_length=50, null=True, blank=True)
    fb_name = models.CharField(max_length=60, null=True, blank=True)
    friends = models.ManyToManyField('self', symmetrical=True)
    join_date = models.DateField()

    def __unicode__(self):
        return 'User profile: ' + self.user.username + ', ' + self.user.first_name + ' ' + self.user.last_name

    def gravator_url(self):
        return "http://www.gravatar.com/avatar/%s?s=50" % hashlib.md5(self.user.email).hexdigest()

    class Meta:
        get_latest_by = "join_date"
        ordering = ['user']
        verbose_name = "User profile"
        verbose_name_plural = "User profiles"


def get_or_create_userprofile(user):
    if user:
        # up = get_object_or_404(UserProfile, user=user)
        try:
            up = UserProfile.objects.get(user=user)
            if up:
                return up
        except ObjectDoesNotExist:
            pass
    up = UserProfile(user=user, join_date=timezone.now())
    up.save()
    return up


User.profile = property(lambda u: get_or_create_userprofile(user=u))
