# Generated by Django 4.2 on 2024-11-28 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0056_projectfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectfile',
            name='file_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]