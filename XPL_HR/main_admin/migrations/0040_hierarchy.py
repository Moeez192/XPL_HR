# Generated by Django 4.2 on 2024-10-24 06:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0039_remove_employee_salary'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hierarchy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval_for', models.CharField(choices=[('leave', 'Leave'), ('timesheet', 'Timesheet')], max_length=50)),
                ('position', models.CharField(choices=[('developer', 'Developer'), ('management', 'Management')], max_length=50)),
                ('final_approver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='final_approvals', to='main_admin.employee')),
                ('first_approver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='first_approvals', to='main_admin.employee')),
                ('second_approver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='second_approvals', to='main_admin.employee')),
            ],
        ),
    ]