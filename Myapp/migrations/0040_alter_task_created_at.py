# Generated by Django 5.1.7 on 2025-03-31 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0039_alter_task_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
    ]
