# Generated by Django 5.1.7 on 2025-03-26 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0025_alter_taskstatus_completion_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='role',
            field=models.CharField(default='Employee', max_length=50),
        ),
    ]
