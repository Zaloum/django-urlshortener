# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-02 21:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='URLRedirect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_url', models.URLField(db_index=True)),
                ('times_used', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
