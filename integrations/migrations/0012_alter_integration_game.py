# pylint: skip-file
# Generated by Django 3.2.15 on 2022-09-01 17:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0026_sitesettings_message_of_the_day'),
        ('integrations', '0011_integration_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='integration',
            name='game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='integrations', to='builder.game'),
        ),
    ]
