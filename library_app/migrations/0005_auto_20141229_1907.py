# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0004_quotationfrombook'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quotationfrombook',
            old_name='Book',
            new_name='book',
        ),
    ]
