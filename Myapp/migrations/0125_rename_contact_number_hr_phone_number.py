# Generated by Django 5.2 on 2025-06-17 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0124_team'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hr',
            old_name='contact_number',
            new_name='phone_number',
        ),
    ]
