# Generated by Django 4.2 on 2024-12-07 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_admin', '0131_alter_projects_billing_method_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientinformation',
            name='weekend',
            field=models.CharField(choices=[('Friday/Saturday', 'Friday/Saturday'), ('Saturday/Sunday', 'Saturday/Sunday')], default='Saturday/Sunday', max_length=50),
        ),
        migrations.AddField(
            model_name='clientinformation',
            name='year',
            field=models.CharField(choices=[(2019, '2019'), (2020, '2020'), (2021, '2021'), (2022, '2022'), (2023, '2023'), (2024, '2024'), (2025, '2025'), (2026, '2026'), (2027, '2027'), (2028, '2028'), (2029, '2029'), (2030, '2030'), (2031, '2031'), (2032, '2032'), (2033, '2033'), (2034, '2034'), (2035, '2035'), (2036, '2036'), (2037, '2037'), (2038, '2038'), (2039, '2039'), (2040, '2040'), (2041, '2041'), (2042, '2042'), (2043, '2043'), (2044, '2044'), (2045, '2045'), (2046, '2046'), (2047, '2047'), (2048, '2048'), (2049, '2049'), (2050, '2050'), (2051, '2051'), (2052, '2052'), (2053, '2053'), (2054, '2054'), (2055, '2055'), (2056, '2056'), (2057, '2057'), (2058, '2058'), (2059, '2059'), (2060, '2060'), (2061, '2061'), (2062, '2062'), (2063, '2063'), (2064, '2064'), (2065, '2065'), (2066, '2066'), (2067, '2067'), (2068, '2068'), (2069, '2069'), (2070, '2070'), (2071, '2071'), (2072, '2072'), (2073, '2073'), (2074, '2074')], default='2024', max_length=4),
        ),
        migrations.AlterField(
            model_name='projects',
            name='billing_method',
            field=models.CharField(choices=[('Fixed Price', 'Fixed Price'), ('Time & Material', 'Time & Material')], default='Fixed Price', max_length=20),
        ),
    ]
