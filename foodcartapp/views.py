import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError

from .models import Product, Order, OrderItem


ORDER_FIELDS = ['products', 'firstname', 'lastname', 'phonenumber', 'address']


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    try:
        order_description = request.data
    except ValueError:
        return Response({
            'error': 'Some ValueError',
        })
    missing_fields = []
    not_valid_strings = []
    result_message = ""

    for field in ORDER_FIELDS:
        try:
            order_description[field]
        except KeyError:
            missing_fields.append(field)
    if missing_fields:
        return Response({
            f'{", ".join(missing_fields)}: обязательное поле.',
        })

    for field in ORDER_FIELDS:
        value = order_description[field]
        if field == 'products' and not value and isinstance(order_description[field], list):
            return Response({
                f'{field}: этот список не может быть пустым.',
            })
        elif not value and isinstance(order_description[field], str) or value is None:
            missing_fields.append(field)

        if field != 'products' and value is not None and not isinstance(order_description[field], str):
            not_valid_strings.append(field)

    if not_valid_strings:
        result_message += f'{", ".join(not_valid_strings)}: недопустимая строка, '
    if missing_fields:
        result_message += f'{", ".join(missing_fields)}: это поле не может быть пустым.'
    if result_message:
        return Response({result_message})

    if isinstance(order_description['products'], str):
        return Response({
            'products: ожидался list со значениями, но был получен "str".',
        })

    for product in order_description['products']:
        if product['product'] > Product.objects.order_by('-pk').first().pk:
            return Response({
                f'products: недопустимый первичный ключ "{product["product"]}"',
            })

    try:
        validate_international_phonenumber(order_description['phonenumber'])
    except ValidationError:
        return Response({
            'phonenumber: введен некорректный номер телефона.',
        })



    order = Order.objects.create(
        address=order_description['address'],
        lastname=order_description['lastname'],
        firstname=order_description['firstname'],
        phonenumber=order_description['phonenumber'],
    )
    for product in order_description['products']:
        OrderItem.objects.create(
            order=order,
            product=Product.objects.filter(pk=product['product']).first(),
            quantity=product['quantity'],
        )
    return Response({})
