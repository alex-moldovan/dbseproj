# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-06 13:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0012_auto_20170304_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='market',
            name='current_day_size',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='market',
            name='day_size_avg',
            field=models.IntegerField(default=0),
        ),
    ]