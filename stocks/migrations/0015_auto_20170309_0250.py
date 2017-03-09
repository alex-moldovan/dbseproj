# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-09 02:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0014_auto_20170307_2059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='market',
            name='days',
        ),
        migrations.AddField(
            model_name='alert',
            name='occur_date',
            field=models.DateField(db_index=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='alert',
            name='sector',
            field=models.CharField(db_index=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='symbol',
            field=models.CharField(db_index=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='market',
            name='tda_price_avg',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
        migrations.AlterField(
            model_name='alert',
            name='trade',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='stocks.Trade'),
        ),
    ]