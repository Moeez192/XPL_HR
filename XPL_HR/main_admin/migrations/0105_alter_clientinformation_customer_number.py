# Generated by Django 4.2 on 2024-12-05 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0104_alter_clientinformation_customer_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientinformation',
            name='customer_number',
            field=models.TextField(max_length=20),
        ),
    ]