# Generated by Django 4.2 on 2024-12-05 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0100_alter_employee_emergency_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='password',
            field=models.CharField(blank=True, default='Progrc@123', max_length=255),
        ),
    ]
