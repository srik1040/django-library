# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('library_app', '0003_auto_20141218_1200'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuotationFromBook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quotation', models.CharField(max_length=600)),
                ('creation_date', models.DateField()),
                ('Book', models.ForeignKey(to='library_app.Book')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['quotation'],
                'get_latest_by': 'creation_date',
                'verbose_name': 'Quotation',
                'verbose_name_plural': 'Quotations',
            },
            bases=(models.Model,),
        ),
    ]
