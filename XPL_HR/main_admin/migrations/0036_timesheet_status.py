# Generated by Django 4.2 on 2024-10-22 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0035_timesheet'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheet',
            name='status',
            field=models.CharField(default='pending', max_length=20),
        ),
    ]