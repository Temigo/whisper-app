# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-20 18:41
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='graph',
            name='data',
            field=jsonfield.fields.JSONField(default='{}'),
        ),
    ]