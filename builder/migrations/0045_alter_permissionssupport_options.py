# pylint: skip-file
# Generated by Django 4.2.11 on 2024-04-22 17:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0044_alter_permissionssupport_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='permissionssupport',
            options={'default_permissions': (), 'managed': False, 'permissions': (('builder_login', 'Access Hive Mechanic game builder'), ('builder_auth_access_view', 'View user account information'), ('builder_auth_access_edit', 'Edit user account information'), ('builder_access_view', 'View game builder information'), ('builder_access_edit', 'Edit game builder information'), ('builder_db_logging_view', 'View database logging entries'), ('builder_db_logging_edit', 'Edit database logging entries'), ('builder_moderate', 'Moderate all content'), ('builder_moderate_activity', 'Moderate activity content'))},
        ),
    ]
