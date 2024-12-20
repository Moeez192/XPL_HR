# Generated by Django 4.2 on 2024-12-05 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0109_alter_employee_nationality'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientinformation',
            name='country_region',
            field=models.CharField(choices=[('pakistan', 'Pakistan'), ('uae', 'UAE'), ('india', 'India')], max_length=50),
        ),
        migrations.AlterField(
            model_name='employee',
            name='nationality',
            field=models.CharField(choices=[('pakistan', 'Pakistan'), ('uae', 'UAE'), ('india', 'India')], max_length=100),
        ),
    ]
