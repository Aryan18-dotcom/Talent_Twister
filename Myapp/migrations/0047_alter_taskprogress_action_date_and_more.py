# Generated by Django 5.1.7 on 2025-03-31 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0046_alter_task_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskprogress',
            name='action_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='taskprogress',
            name='completion_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
