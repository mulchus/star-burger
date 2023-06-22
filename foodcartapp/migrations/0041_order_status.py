# Generated by Django 3.2.15 on 2023-06-22 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20230617_0014'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Уточняется', 'Уточняется'), ('Собирается', 'Собирается'), ('Доставляется', 'Доставляется'), ('Выполнен', 'Выполнен')], db_index=True, default='Уточняется', max_length=12, verbose_name='статус'),
        ),
    ]
