# Generated by Django 5.2 on 2025-07-08 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0161_co_curricular_discription_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='co_curricular',
            name='proficiency',
            field=models.IntegerField(),
        ),
    ]
