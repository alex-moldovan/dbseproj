# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-02 14:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0005_auto_20170302_0727'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='checked',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
