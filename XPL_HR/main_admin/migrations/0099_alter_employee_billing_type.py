# Generated by Django 4.2 on 2024-12-04 07:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0098_alter_employee_bank_country_alter_employee_bonus_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='billing_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='billing_type_table', to='main_admin.billingtype'),
        ),
    ]