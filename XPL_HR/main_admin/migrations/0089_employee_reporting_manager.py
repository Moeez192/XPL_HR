# Generated by Django 4.2 on 2024-12-02 04:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0088_alter_employee_skills'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='reporting_manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='report_to_manager', to='main_admin.employee'),
        ),
    ]
