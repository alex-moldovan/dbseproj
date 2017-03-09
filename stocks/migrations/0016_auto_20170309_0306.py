# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-09 03:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0015_auto_20170309_0250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='buyer',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='trade',
            name='sector',
            field=models.CharField(db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='trade',
            name='seller',
            field=models.EmailField(max_length=254),
        ),
    ]