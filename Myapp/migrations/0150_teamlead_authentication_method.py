# Generated by Django 5.2 on 2025-07-06 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0149_alter_teamlead_about_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamlead',
            name='authentication_method',
            field=models.CharField(blank=True, choices=[('Email', 'Email'), ('SMS', 'SMS'), ('Authenticator App', 'Authenticator App')], default='Email', max_length=20, null=True),
        ),
    ]
