# Generated by Django 4.2.11 on 2024-03-29 18:09

from django.db import migrations, models

import django.contrib.postgres.fields.jsonb

class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0041_statevariable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statevariable',
            name='metadata',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
    ]
# pylint: skip-file
