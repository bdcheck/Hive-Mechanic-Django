# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-13 18:25


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0006_interactioncard_client_implementation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameversion',
            name='definition',
            field=models.TextField(db_index=True, max_length=1073741824),
        ),
    ]
