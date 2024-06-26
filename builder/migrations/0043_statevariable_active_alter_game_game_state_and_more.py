# pylint: skip-file
# Generated by Django 4.2.11 on 2024-04-12 18:03

from django.db import migrations, models

import django.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0042_alter_statevariable_metadata'),
    ]

    operations = [
        migrations.AddField(
            model_name='statevariable',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='game_state',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='game',
            name='metadata',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='player',
            name='player_state',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_state',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='statevariable',
            name='metadata',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='statevariable',
            name='value',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
