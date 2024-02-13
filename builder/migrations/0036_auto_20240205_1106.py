# pylint: skip-file
# Generated by Django 3.2.23 on 2024-02-05 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # ('filer', '0015_auto_20240205_1106'),
        ('builder', '0035_alter_dataprocessor_log_summary_function'),
    ]

    operations = [
        migrations.CreateModel(
            name='CachedFile',
            fields=[
                ('file_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='filer.file')),
                ('original_url', models.CharField(max_length=4096)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('filer.file',),
        ),
        migrations.AlterField(
            model_name='dataprocessor',
            name='log_summary_function',
            field=models.TextField(default='None', help_text='Generates summary of data processor API calls, in a human-readable format.', max_length=1048576),
        ),
    ]
