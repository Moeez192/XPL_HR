# Generated by Django 4.2 on 2024-10-17 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0010_remove_employee_supervisor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='is_supervisor',
            field=models.CharField(choices=[('yes', 'Yes'), ('no', 'No')], max_length=20),
        ),
    ]
