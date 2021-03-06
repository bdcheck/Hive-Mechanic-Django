# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-16 03:27

from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('integrations', '0003_auto_20200403_1522'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4096, unique=True)),
                ('shared_secret', models.CharField(max_length=4096, unique=True)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('integration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_clients', to='integrations.Integration')),
            ],
        ),
    ]
