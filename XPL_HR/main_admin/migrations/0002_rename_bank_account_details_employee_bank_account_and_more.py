# Generated by Django 5.0.2 on 2024-10-16 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='bank_account_details',
            new_name='bank_account',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='emergency_contact_name',
            new_name='emergency_name',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='emergency_contact_relation',
            new_name='emergency_relation',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='emergency_contact_phone',
        ),
        migrations.AddField(
            model_name='employee',
            name='emergency_phone',
            field=models.CharField(default='Not Provided', max_length=12),
        ),
        migrations.AlterField(
            model_name='employee',
            name='employee_status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('on-leave', 'On Leave'), ('terminated', 'Terminated')], max_length=20),
        ),
        migrations.AlterField(
            model_name='employee',
            name='employment_type',
            field=models.CharField(choices=[('full-time', 'Full-Time'), ('part-time', 'Part-Time'), ('contract', 'Contract'), ('intern', 'Intern')], max_length=20),
        ),
        migrations.AlterField(
            model_name='employee',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10),
        ),
        migrations.AlterField(
            model_name='employee',
            name='nationality',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='employee',
            name='password',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='employee',
            name='phone',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='employee',
            name='work_location',
            field=models.CharField(max_length=255),
        ),
    ]
