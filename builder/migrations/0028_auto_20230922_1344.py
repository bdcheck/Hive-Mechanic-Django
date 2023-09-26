# pylint: skip-file
# Generated by Django 3.2.20 on 2023-09-22 17:44

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0027_alter_sitesettings_total_message_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='metadata',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='game',
            name='metadata_updated',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
