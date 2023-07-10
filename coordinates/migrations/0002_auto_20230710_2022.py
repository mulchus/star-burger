# Generated by Django 3.2.15 on 2023-07-10 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinates', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='lat',
            field=models.FloatField(blank=True, db_index=True, null=True, verbose_name='широта'),
        ),
        migrations.AlterField(
            model_name='location',
            name='lon',
            field=models.FloatField(blank=True, db_index=True, null=True, verbose_name='долгота'),
        ),
    ]
