# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-02 07:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0004_auto_20170302_0333'),
    ]

    operations = [
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_date', models.DateField(db_index=True)),
                ('symbol', models.CharField(db_index=True, max_length=10)),
                ('price_avg', models.DecimalField(decimal_places=2, max_digits=7)),
                ('price_stddev', models.DecimalField(decimal_places=2, max_digits=7)),
                ('size_avg', models.IntegerField(default=0)),
                ('size_stddev', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_date', models.DateField(db_index=True)),
                ('sector', models.CharField(db_index=True, max_length=50)),
                ('price_avg', models.DecimalField(decimal_places=2, max_digits=7)),
                ('price_stddev', models.DecimalField(decimal_places=2, max_digits=7)),
                ('size_avg', models.IntegerField(default=0)),
                ('size_stddev', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='trade',
            name='symbol',
            field=models.CharField(db_index=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='trade',
            name='trade_time',
            field=models.DateTimeField(db_index=True),
        ),
    ]
