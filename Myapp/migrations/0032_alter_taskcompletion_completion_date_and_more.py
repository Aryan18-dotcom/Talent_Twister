# Generated by Django 5.1.7 on 2025-03-30 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0031_alter_taskcompletion_completion_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskcompletion',
            name='completion_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='taskstatus',
            name='action_date',
            field=models.DateField(),
        ),
    ]
