# Generated by Django 4.2 on 2024-12-01 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0079_alter_employee_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='days_from_latest_entry',
            field=models.CharField(default='none', max_length=50),
        ),
    ]
