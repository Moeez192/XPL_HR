# Generated by Django 4.2 on 2024-12-14 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0148_alter_projects_billing_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='leave_policy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_leave_policy', to='main_admin.leaves'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='billing_method',
            field=models.CharField(choices=[('Fixed Price', 'Fixed Price'), ('Time & Material', 'Time & Material')], default='Fixed Price', max_length=20),
        ),
    ]