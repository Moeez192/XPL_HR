# Generated by Django 4.2 on 2024-10-21 05:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0031_rename_position_employee_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationalDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_name', models.CharField(max_length=255)),
                ('document_file', models.FileField(upload_to='documents/')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_admin.employee')),
            ],
        ),
    ]