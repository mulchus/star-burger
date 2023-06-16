# Generated by Django 3.2.15 on 2023-06-16 21:14

from django.db import migrations


def set_fix_price(apps, schema_editor):
    OrderItem = apps.get_model('foodcartapp', 'OrderItem')
    for orderitem in OrderItem.objects.all():
        if not orderitem.product_fix_price:
            orderitem.product_fix_price = orderitem.product.price
            orderitem.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_auto_20230616_2339'),
    ]

    operations = [
        migrations.RunPython(set_fix_price),
    ]