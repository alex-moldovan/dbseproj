# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-02 18:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0008_alert'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='resolved',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
