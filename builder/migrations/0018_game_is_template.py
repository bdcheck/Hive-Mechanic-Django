# pylint: skip-file
# Generated by Django 3.2.7 on 2021-12-16 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0017_sitesettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='is_template',
            field=models.BooleanField(default=False),
        ),
    ]
