# Generated by Django 4.2 on 2024-12-05 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0107_alter_clientinformation_enable_portal_access'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientinformation',
            name='enable_portal_access',
            field=models.TextField(choices=[('yes', 'Yes'), ('no', 'No')]),
        ),
    ]