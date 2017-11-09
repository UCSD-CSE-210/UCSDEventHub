# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(null=True)),
                ('location', models.CharField(max_length=255)),
                ('date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('image', models.ImageField(upload_to='')),
                ('hastags', models.CharField(max_length=255)),
                ('organizer', models.CharField(max_length=255)),
                ('contact_email', models.EmailField(max_length=254)),
            ],
        ),
    ]
