# pylint: skip-file
# Generated by Django 3.2.24 on 2024-03-08 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0037_alter_cachedfile_original_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='archived',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
