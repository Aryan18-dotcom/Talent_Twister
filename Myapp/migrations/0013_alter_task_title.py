# Generated by Django 5.1.7 on 2025-03-22 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0012_alter_task_assigned_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
