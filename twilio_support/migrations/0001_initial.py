# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-12 20:42

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('integrations', '0002_integration_create_new_players'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomingMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=256)),
                ('receive_date', models.DateTimeField()),
                ('message', models.TextField(max_length=1024)),
                ('transmission_metadata', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('integration', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='twilio_incoming', to='integrations.Integration')),
            ],
        ),
        migrations.CreateModel(
            name='OutgoingMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destination', models.CharField(max_length=256)),
                ('send_date', models.DateTimeField()),
                ('sent_date', models.DateTimeField(blank=True, null=True)),
                ('message', models.TextField(max_length=1024)),
                ('errored', models.BooleanField(default=False)),
                ('transmission_metadata', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('integration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='twilio_outgoing', to='integrations.Integration')),
            ],
        ),
    ]
