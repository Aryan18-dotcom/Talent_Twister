# Generated by Django 5.1.7 on 2025-03-24 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0018_taskstatus_finesh_alter_taskstatus_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskstatus',
            name='finesh',
            field=models.CharField(choices=[('Complete', 'complete'), ('InComplete', 'inComplete')], default='Incomplete', max_length=10),
        ),
        migrations.AlterField(
            model_name='taskstatus',
            name='status',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('Postponed', 'Postponed')], max_length=10),
        ),
    ]
