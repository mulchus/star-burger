# from rest_framework.serializers import ModelSerializer
# from rest_framework.serializers import ListField
from rest_framework import serializers
from .models import Order, OrderItem, Product
from phonenumber_field.modelfields import PhoneNumberField


class OrderItemSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        print('CREATE ITEMS')
        return OrderItem.objects.bulk_create(**validated_data)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False)
    # print(products)

    def create(self, validated_data):
        print('CREATE')
        return Order.objects.create(**validated_data)

    class Meta:
        model = Order
        fields = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
