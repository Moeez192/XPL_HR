# Generated by Django 4.2 on 2024-11-30 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0071_alter_employee_mol_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='uploadDocType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_type', models.CharField(max_length=20)),
            ],
        ),
    ]