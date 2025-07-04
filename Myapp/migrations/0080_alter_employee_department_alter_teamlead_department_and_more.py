# Generated by Django 5.2 on 2025-05-07 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0079_teamlead_about_teamlead_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.CharField(choices=[('General', 'General'), ('HR', 'Human Resources'), ('Engineering', 'Engineering'), ('Sales', 'Sales'), ('Marketing', 'Marketing'), ('Support', 'Customer Support'), ('Finance', 'Finance'), ('IT', 'Information Technology'), ('Legal', 'Legal'), ('Operations', 'Operations'), ('Product', 'Product Management'), ('Design', 'Design'), ('Research', 'Research and Development'), ('Quality Assurance', 'Quality Assurance'), ('Administration', 'Administration'), ('Logistics', 'Logistics'), ('Public Relations', 'Public Relations'), ('Training', 'Training and Development'), ('Procurement', 'Procurement'), ('Compliance', 'Compliance'), ('Data Science', 'Data Science')], default='General', max_length=50),
        ),
        migrations.AlterField(
            model_name='teamlead',
            name='department',
            field=models.CharField(choices=[('General', 'General'), ('HR', 'Human Resources'), ('Engineering', 'Engineering'), ('Sales', 'Sales'), ('Marketing', 'Marketing'), ('Support', 'Customer Support'), ('Finance', 'Finance'), ('IT', 'Information Technology'), ('Legal', 'Legal'), ('Operations', 'Operations'), ('Product', 'Product Management'), ('Design', 'Design'), ('Research', 'Research and Development'), ('Quality Assurance', 'Quality Assurance'), ('Administration', 'Administration'), ('Logistics', 'Logistics'), ('Public Relations', 'Public Relations'), ('Training', 'Training and Development'), ('Procurement', 'Procurement'), ('Compliance', 'Compliance'), ('Data Science', 'Data Science')], default='General', max_length=50),
        ),
        migrations.AlterField(
            model_name='teamlead',
            name='role',
            field=models.CharField(default='Team Leader', max_length=50),
        ),
    ]
