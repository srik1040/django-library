from django.contrib import admin
from .models import *
# from django.contrib.contenttypes.models import ContentType

# Register your models here.

admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(LendPeriods)
admin.site.register(Book)
admin.site.register(UserProfile)
admin.site.register(QuotationFromBook)
# admin.site.register(ContentType)