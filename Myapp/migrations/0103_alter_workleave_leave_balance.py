# Generated by Django 5.2 on 2025-05-20 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0102_alter_workleave_leave_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workleave',
            name='leave_balance',
            field=models.IntegerField(blank=True, default=20, null=True),
        ),
    ]
