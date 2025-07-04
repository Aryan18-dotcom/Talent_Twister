# Generated by Django 5.2 on 2025-05-07 12:47

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0078_rename_leves_employee_leave_remove_employee_logedin_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamlead',
            name='about',
            field=models.TextField(blank=True, max_length=175, null=True),
        ),
        migrations.AddField(
            model_name='teamlead',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='teamlead',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='teamlead',
            name='department',
            field=models.CharField(choices=[('General', 'General'), ('HR', 'Human Resources'), ('Engineering', 'Engineering'), ('Sales', 'Sales'), ('Marketing', 'Marketing'), ('Support', 'Customer Support'), ('Finance', 'Finance')], default='General', max_length=50),
        ),
        migrations.AddField(
            model_name='teamlead',
            name='emergency_contact',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='teamlead',
            name='gender',
            field=models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='teamlead',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='teamlead',
            name='joining_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='teamlead',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='teamlead',
            name='leave',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='teamlead',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='teamlead',
            name='role',
            field=models.CharField(default='Employee', max_length=50),
        ),
        migrations.AddField(
            model_name='teamlead',
            name='teamLead_id',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]
