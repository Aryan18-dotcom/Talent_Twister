# Generated by Django 5.2 on 2025-04-10 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0068_employee_leves'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='logedin',
            field=models.BooleanField(default=False),
        ),
    ]
