# Generated by Django 5.2 on 2025-04-10 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0069_employee_logedin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='logedin',
            field=models.IntegerField(default=False),
        ),
    ]
