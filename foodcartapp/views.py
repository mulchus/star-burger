import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
    for field in ORDER_FIELDS:
        try:
            value = order_description[field]
        except KeyError:
            return Response({
                f'{field}: Обязательное поле.',
            })
        if not value and field == 'products' and isinstance(order_description['products'], list):
            return Response({
                'products: Этот список не может быть пустым.',
            })
        elif not value:
            return Response({
                f'{field}: Это поле не может быть пустым.',
            })
        elif not isinstance(order_description['products'][0], dict) and field == 'products' and isinstance(order_description['products'], list):
            return Response({
                'products: В списке данные не имеют тип словаря.',
            })

    if isinstance(order_description['products'], str):
        return Response({
            'products: Ожидался list со значениями, но был получен "str".',
        })


    # for key in dict(order_description).keys():
    #     if not order_description[key]:
    #         return Response({
    #             f'{key}: Это поле не может быть пустым.',
    #         })

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
