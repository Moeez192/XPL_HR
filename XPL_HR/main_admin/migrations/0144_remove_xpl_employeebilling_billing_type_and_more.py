# Generated by Django 4.2 on 2024-12-12 07:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0143_remove_timesheet_is_editable_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='xpl_employeebilling',
            name='billing_type',
        ),
        migrations.AddField(
            model_name='xpl_employeebilling',
            name='billing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main_admin.billingtype'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='billing_method',
            field=models.CharField(choices=[('Fixed Price', 'Fixed Price'), ('Time & Material', 'Time & Material')], default='Fixed Price', max_length=20),
        ),
    ]
