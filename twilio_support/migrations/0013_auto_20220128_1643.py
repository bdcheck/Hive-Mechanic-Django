# pylint: skip-file
# Generated by Django 3.2.10 on 2022-01-28 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twilio_support', '0012_merge_20211228_1953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outgoingcall',
            name='gather_finish_on_key',
            field=models.CharField(default='#', max_length=64),
        ),
        migrations.AlterField(
            model_name='outgoingcall',
            name='gather_num_digits',
            field=models.IntegerField(default=4),
        ),
        migrations.AlterField(
            model_name='outgoingcall',
            name='gather_speech_timeout',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='outgoingcall',
            name='gather_timeout',
            field=models.IntegerField(default=5),
        ),
    ]