# Generated by Django 5.0.1 on 2024-02-18 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0003_booking_end_date_booking_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='start_date',
            field=models.DateField(null=True),
        ),
    ]
