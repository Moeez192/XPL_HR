# Generated by Django 4.2 on 2024-10-17 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0017_alter_employee_employee_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
