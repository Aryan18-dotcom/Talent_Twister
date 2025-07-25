# Generated by Django 5.2 on 2025-06-25 11:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0138_alter_co_curricular_hr'),
    ]

    operations = [
        migrations.AddField(
            model_name='co_curricular',
            name='proficiency',
            field=models.PositiveSmallIntegerField(default=1, help_text='Rate proficiency from 1 (Beginner) to 5 (Expert)', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
