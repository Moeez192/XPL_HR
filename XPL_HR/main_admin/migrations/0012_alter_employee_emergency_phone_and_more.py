# Generated by Django 4.2 on 2024-10-17 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0011_alter_employee_is_supervisor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='emergency_phone',
            field=models.CharField(max_length=12),
        ),
        migrations.AlterField(
            model_name='employee',
            name='password',
            field=models.CharField(blank=True, default='pakistan', max_length=255),
        ),
    ]