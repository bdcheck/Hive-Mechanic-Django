# pylint: skip-file
# Generated by Django 3.2.7 on 2021-10-22 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twilio_support', '0008_remove_outgoingcall_start_call'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingcallresponse',
            name='message',
            field=models.TextField(blank=True, max_length=1024, null=True),
        ),
    ]
