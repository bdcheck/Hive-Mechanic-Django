# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-25 02:38


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('twilio_support', '0004_auto_20191011_2044'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomingMessageMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField(default=0)),
                ('content_file', models.FileField(blank=True, null=True, upload_to='incoming_message_media')),
                ('content_url', models.CharField(blank=True, max_length=1024, null=True)),
                ('content_type', models.CharField(default='application/octet-stream', max_length=128)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to='twilio_support.IncomingMessage')),
            ],
        ),
    ]
