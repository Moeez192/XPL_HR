# Generated by Django 4.2 on 2024-10-21 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0033_educationaldocument_file_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaveapplication',
            name='remarks',
            field=models.TextField(blank=True, null=True),
        ),
    ]