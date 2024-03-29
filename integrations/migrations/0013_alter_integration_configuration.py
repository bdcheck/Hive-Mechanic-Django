# pylint: skip-file
# Generated by Django 4.2.10 on 2024-03-08 20:18

import sys

from django.db import migrations, models



class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0012_alter_integration_game'),
    ]

    if sys.version_info[0] > 2:
        operations = [
            migrations.AlterField(
                model_name='integration',
                name='configuration',
                field=models.JSONField(blank=True, default=dict, help_text='configuration_help_text', null=True),
            ),
        ]
    else:
        operations = []
