# pylint: skip-file
# Generated by Django 3.2.7 on 2021-11-15 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0016_game_icon'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('banner', models.ImageField(blank=True, null=True, upload_to='site_banners')),
                ('created', models.DateTimeField()),
                ('last_updated', models.DateTimeField()),
            ],
        ),
    ]
