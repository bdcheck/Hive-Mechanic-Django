# pylint: skip-file
# Generated by Django 3.2.23 on 2024-01-05 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0031_auto_20240105_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataprocessorlog',
            name='context',
            field=models.TextField(blank=True, max_length=4194304, null=True),
        ),
    ]