# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-12 20:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='integration',
            name='create_new_players',
            field=models.BooleanField(default=True),
        ),
    ]
