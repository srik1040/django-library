# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0002_auto_20141218_1051'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='author',
            options={'ordering': ['name', 'surname'], 'get_latest_by': 'name', 'verbose_name': 'Author', 'verbose_name_plural': 'Authors'},
        ),
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['title'], 'verbose_name': 'Book', 'verbose_name_plural': 'Books'},
        ),
        migrations.AlterModelOptions(
            name='lendperiods',
            options={'ordering': ['days_amount'], 'get_latest_by': 'days_amount', 'verbose_name': 'Lending period', 'verbose_name_plural': 'Lending periods'},
        ),
        migrations.AlterModelOptions(
            name='publisher',
            options={'ordering': ['name'], 'get_latest_by': 'name', 'verbose_name': 'Publisher', 'verbose_name_plural': 'Publishers'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'ordering': ['user'], 'get_latest_by': 'join_date', 'verbose_name': 'User profile', 'verbose_name_plural': 'User profiles'},
        ),
        migrations.AlterField(
            model_name='book',
            name='lend_by',
            field=models.ForeignKey(blank=True, to='library_app.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='book',
            name='lend_from',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
