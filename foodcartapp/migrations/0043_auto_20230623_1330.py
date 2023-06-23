# Generated by Django 3.2.15 on 2023-06-23 10:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='called_datetime',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='созвонились'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivered_datetime',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='доставлен'),
        ),
        migrations.AddField(
            model_name='order',
            name='registered_datetime',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='зарегистрирован'),
        ),
    ]
