# Generated by Django 5.2 on 2025-05-20 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0110_workleave_is_half_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='workleave',
            name='half_day_period',
            field=models.CharField(choices=[('First Half', 'First Half'), ('Second Half', 'Second Half')], default='First Half', max_length=20),
        ),
    ]
