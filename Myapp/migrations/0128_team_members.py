# Generated by Django 5.2 on 2025-06-17 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0127_rename_profile_picture_hr_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='teams', to='Myapp.employee'),
        ),
    ]
