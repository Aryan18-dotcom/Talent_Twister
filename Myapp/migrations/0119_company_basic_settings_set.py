# Generated by Django 5.2 on 2025-06-09 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0118_company_address_company_allow_custom_themes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='basic_settings_set',
            field=models.BooleanField(default=False),
        ),
    ]
