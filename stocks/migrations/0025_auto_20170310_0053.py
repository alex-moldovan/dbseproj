# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-10 00:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0024_auto_20170309_2112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='market',
            name='update_date',
            field=models.DateTimeField(db_index=True),
        ),
    ]
