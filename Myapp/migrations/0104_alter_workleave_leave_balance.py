# Generated by Django 5.2 on 2025-05-20 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0103_alter_workleave_leave_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workleave',
            name='leave_balance',
            field=models.IntegerField(default=20),
        ),
    ]
