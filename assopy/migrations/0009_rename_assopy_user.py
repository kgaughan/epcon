
# Generated by Django 1.11.16 on 2018-10-27 10:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    # Disabling atomicity in the transaction due to following error. Once the production db gets upgraded,
    # we can reenable atomicity.
    # django.db.utils.NotSupportedError: Renaming the 'assopy_user' table while in a transaction is not supported
    # on SQLite < 3.26 because it would break referential integrity. Try adding `atomic = False` to the Migration class.
    atomic = False

    dependencies = [
        ('assopy', '0008_remove_user_oauth_info_model'),
        ('p3', '0002_remove_unused_models'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='AssopyUser',
        ),
    ]
