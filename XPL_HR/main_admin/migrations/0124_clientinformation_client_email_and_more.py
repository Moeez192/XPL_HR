# Generated by Django 4.2 on 2024-12-06 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0123_remove_employee_is_supervisor'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientinformation',
            name='client_email',
            field=models.EmailField(default='none', max_length=254),
        ),
        migrations.AddField(
            model_name='clientinformation',
            name='first_name',
            field=models.CharField(default='none', max_length=50),
        ),
        migrations.AddField(
            model_name='clientinformation',
            name='last_name',
            field=models.CharField(default='none', max_length=50),
        ),
    ]