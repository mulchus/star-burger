from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from .serializers import OrderSerializer, OrderItemSerializer
from .models import Product, Order, OrderItem


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


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    order_serializer = OrderSerializer(data=request.data)
    order_serializer.is_valid(raise_exception=True)
    order = order_serializer.create(order_serializer.validated_data)
    print(order_serializer)
    print(order)

    order_items_fields = order_serializer.validated_data['products']
    # order_items_fields = request.data.get('products', [])

    # product_serializer = OrderItemSerializer(data=request.data['products'], many=True, allow_empty=False)
    # product_serializer.is_valid(raise_exception=True)
    # products = product_serializer.save()
    # print(products)

    print(order_items_fields)
    # order_items = [OrderItem(order=order, **products) for products in order_items_fields]
    # OrderItem.objects.bulk_create(order_items)
    # order = order_serializer.create()

    return Response({
        'id': order.id,
        'firstname': order.firstname,
        'lastname': order.lastname,
        'phonenumber': str(order.phonenumber),
        'address': order.address,
    })
