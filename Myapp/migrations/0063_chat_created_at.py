# Generated by Django 5.2 on 2025-04-06 09:47

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0062_alter_employee_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
