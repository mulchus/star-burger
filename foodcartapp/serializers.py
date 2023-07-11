# from rest_framework.serializers import ModelSerializer
# from rest_framework.serializers import ListField
from rest_framework import serializers
from .models import Order, OrderItem, Product
from phonenumber_field.modelfields import PhoneNumberField


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False)

    def create(self, validated_data):
        order = Order.objects.create(
            address=validated_data['address'],
            lastname=validated_data['lastname'],
            firstname=validated_data['firstname'],
            phonenumber=validated_data['phonenumber'],
        )

        order_items_fields = validated_data['products']
        order_items = [OrderItem(order=order, **products) for products in order_items_fields]
        OrderItem.objects.bulk_create(order_items)
        return order

    class Meta:
        model = Order
        fields = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
