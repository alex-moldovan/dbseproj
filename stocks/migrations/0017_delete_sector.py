# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-09 03:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0016_auto_20170309_0306'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Sector',
        ),
    ]
