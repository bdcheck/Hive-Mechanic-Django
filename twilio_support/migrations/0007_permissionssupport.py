# pylint: skip-file
# Generated by Django 2.2.16 on 2021-01-15 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twilio_support', '0006_auto_20201016_0413'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermissionsSupport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('twilio_history_access', 'Access Twilio message history'),),
                'managed': False,
                'default_permissions': (),
            },
        ),
    ]
