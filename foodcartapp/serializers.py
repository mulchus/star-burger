from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False)

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for order_item in products_data:
            OrderItem.objects.create(order=order, **order_item)
        return order

    class Meta:
        model = Order
        fields = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
