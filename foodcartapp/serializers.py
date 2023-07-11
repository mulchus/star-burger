# from rest_framework.serializers import ModelSerializer
# from rest_framework.serializers import ListField
from rest_framework import serializers
from .models import Order, OrderItem, Product
from phonenumber_field.modelfields import PhoneNumberField


class OrderItemSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        print('CREATE ITEMS')
        print(f'**validated_data {validated_data}')
        return OrderItem.objects.bulk_create(**validated_data)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False)
    print(f'products {products}')

    def create(self, validated_data):
        print('CREATE')
        print(f'**validated_data {validated_data}')
        return Order.objects.create(**validated_data)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address']
