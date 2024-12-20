# Generated by Django 4.2 on 2024-12-07 06:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0129_projects_billing_method_projects_project_budget_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projects',
            name='billing_method',
            field=models.CharField(choices=[('Fixed Price', 'Fixed Price'), ('Time & Material', 'Time & Material')], default='Fixed Price', max_length=20),
        ),
        migrations.AlterField(
            model_name='projects',
            name='client_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client_name', to='main_admin.clientinformation'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='project_budget',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='projects',
            name='project_location',
            field=models.CharField(max_length=256),
        ),
    ]
