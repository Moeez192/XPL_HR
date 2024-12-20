# Generated by Django 4.2 on 2024-10-18 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0018_employee_last_login'),
    ]

    operations = [
        migrations.CreateModel(
            name='Projects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=30)),
                ('client_name', models.CharField(max_length=20)),
                ('project_description', models.CharField(max_length=256)),
                ('start_date', models.DateField()),
                ('deadline', models.DateField()),
                ('requirement_file', models.FileField(upload_to='projects/')),
                ('project_manager', models.CharField(max_length=20)),
                ('team_members', models.CharField(max_length=20)),
                ('is_timesheet_required', models.CharField(choices=[('yes', 'Yes'), ('no', 'No')], max_length=4)),
                ('priority', models.CharField(choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], max_length=20)),
                ('status', models.CharField(choices=[('not started', 'Not Started'), ('in progress', 'In Progress'), ('complete', 'Complete')], max_length=20)),
            ],
        ),
    ]
