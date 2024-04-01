# pylint: skip-file
# Generated by Django 4.2.11 on 2024-03-29 18:05

from django.db import migrations, models
import django.db.models.deletion
import django.contrib.postgres.fields.jsonb

class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0040_remoterepository_enabled'),
    ]

    operations = [
        migrations.CreateModel(
            name='StateVariable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=1024)),
                ('value', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('added', models.DateTimeField()),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='state_variables', to='builder.game')),
                ('player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='state_variables', to='builder.player')),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='state_variables', to='builder.session')),
            ],
        ),
    ]
