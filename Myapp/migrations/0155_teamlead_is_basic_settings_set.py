# Generated by Django 5.2 on 2025-07-07 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0154_jobseeker_is_account_verified_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamlead',
            name='is_basic_settings_set',
            field=models.BooleanField(default=False),
        ),
    ]
