# Generated by Django 5.0.3 on 2024-03-13 13:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Parking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parkingslot',
            name='parking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slots', to='Parking.parking'),
        ),
    ]
