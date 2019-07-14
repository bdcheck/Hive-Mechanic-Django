# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-06-28 20:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InteractionCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4096, unique=True)),
                ('identifier', models.SlugField(max_length=4096, unique=True)),
                ('description', models.TextField(blank=True, max_length=16384, null=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
    ]
