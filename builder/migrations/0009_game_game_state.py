# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-13 19:10
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0008_auto_20190813_1826'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='game_state',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]
