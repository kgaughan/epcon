# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-03-02 21:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conference', '0019_add_stripe_session_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendeeprofile',
            name='gender',
            field=models.CharField(choices=[('m', 'Male'), ('f', 'Female'), ('o', 'Other'), ('x', 'Prefer not to say')], help_text='We use this information for statistics related to conference attendance diversity.', max_length=1),
        ),
        migrations.AlterField(
            model_name='attendeeprofile',
            name='phone',
            field=models.CharField(blank=True, help_text='We require a mobile phone number for all speakers for last minute contacts and in case we need timely clarification (if no reponse to previous emails). Use the international format (e.g.: +44 123456789).', max_length=30, verbose_name='Phone'),
        ),
    ]
