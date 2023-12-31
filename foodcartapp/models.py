import requests

from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.db.models import Prefetch
from django.conf import settings
from geopy import distance
from coordinates.models import Location
from django.core.exceptions import ObjectDoesNotExist


class Restaurant(models.Model):

    name = models.CharField(
        'название',
        max_length=50
    )

    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )

    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):

    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):

    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(
        'название',
        max_length=50
    )

    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    image = models.ImageField(
        'картинка'
    )

    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )

    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):

    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )

    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):

    address = models.CharField(
        'адрес',
        max_length=100,
        db_index=True,
    )

    firstname = models.CharField(
        'имя',
        max_length=30,
        db_index=True,
    )

    lastname = models.CharField(
        'фамилия',
        max_length=30,
        db_index=True,
    )

    phonenumber = PhoneNumberField(
        'мобильный номер:',
        max_length=15,
        db_index=True,
    )

    status = models.CharField(
        'статус',
        max_length=12,
        choices=(
            ("Уточняется", "Уточняется"),
            ("Собирается", "Собирается"),
            ("Доставляется", "Доставляется"),
            ("Выполнен", "Выполнен"),
        ),
        default="Уточняется",
        db_index=True,
    )

    comment = models.TextField(
        'комментарий',
        db_index=True,
        blank=True,
    )

    registered_datetime = models.DateTimeField(
        'зарегистрирован',
        default=timezone.now,
        db_index=True,
    )

    called_datetime = models.DateTimeField(
        'созвонились',
        blank=True,
        null=True,
        db_index=True,
    )

    delivered_datetime = models.DateTimeField(
        'доставлен',
        blank=True,
        null=True,
        db_index=True,
    )

    payment_method = models.CharField(
        'способ оплаты',
        max_length=10,
        choices=(
            ("Наличные", "Наличные"),
            ("Электронно", "Электронно"),
            ("Не указано", "Не указано"),
        ),
        default="Не указано",
        db_index=True,
    )

    selected_restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.lastname} {self.firstname}, {self.address}, {self.phonenumber}'


class OrderItemQuerySet(models.QuerySet):

    def get_orders(self):

        def count_unique(restaurants_ids):
            """
            Возвращает словарь, в котором каждому уникальному элементу списка restaurants_ids соответствует
            количество его повторений.
            """
            repeats = {}
            for restaurant_id in set(restaurants_ids):
                repeats[restaurant_id] = restaurants_ids.count(restaurant_id)
            return repeats

        def fetch_coordinates(apikey, address):
            base_url = "https://geocode-maps.yandex.ru/1.x"
            response = requests.get(base_url, params={
                "geocode": address,
                "apikey": apikey,
                "format": "json",
            })
            response.raise_for_status()
            found_places = response.json()['response']['GeoObjectCollection']['featureMember']

            if not found_places:
                return None

            most_relevant = found_places[0]
            lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
            return lon, lat

        def create_location(address):
            new_loc_coordinates = fetch_coordinates(settings.YANDEX_API_KEY, address)
            if new_loc_coordinates:
                new_loc_lon, new_loc_lat = new_loc_coordinates
            else:
                new_loc_lon, new_loc_lat = 0, 0
            new_location = Location.objects.create(
                address=address,
                lat=new_loc_lat,
                lon=new_loc_lon,
            )
            return new_location

        def get_location(address):
            try:
                location = Location.objects.get(address=address)
            except ObjectDoesNotExist:
                location = create_location(address)
            return location

        # начало основной функции
        menu_entries = RestaurantMenuItem.objects.values()
        product_restaurants_item = {}
        for menu_entry in menu_entries:
            if not menu_entry['product_id'] in product_restaurants_item:
                product_restaurants_item[menu_entry['product_id']] = (menu_entry['restaurant_id'], )
            else:
                product_restaurants_item[menu_entry['product_id']] += (menu_entry['restaurant_id'], )

        items = self.select_related('product')
        for item in items:
            order_restaurant_ids = []
            restaurants = item.product.menu_items.values()
            for restaurant in restaurants:
                order_restaurant_ids.append(restaurant['restaurant_id'])

        orders_to_display = self.exclude(
            order__status__exact='Выполнен').select_related(
            'order', 'product').values(
            'order__pk', 'order__status', 'order__payment_method', 'order__lastname', 'order__firstname',
            'order__address', 'order__comment', 'order__phonenumber', 'order__selected_restaurant__name').annotate(
            total_price=Sum(F('product_fix_price') * F('quantity'))).order_by('-order__status')

        for record in orders_to_display:
            delivery_coordinates = get_location(record['order__address'])
            order_items = OrderItem.objects.filter(order__pk=record['order__pk']).values()
            all_order_restaurants = []
            for order_item in order_items:
                all_order_restaurants.extend(product_restaurants_item[order_item['product_id']])
            unsorted_restaurants = {}
            unique = count_unique(all_order_restaurants)
            for restaurant_id in unique:
                if unique[restaurant_id] == len(order_items):
                    restaurant = Restaurant.objects.get(pk=restaurant_id)
                    restaurant_coordinates = get_location(restaurant.address)
                    if restaurant_coordinates.lat and restaurant_coordinates.lon \
                            and delivery_coordinates.lat and delivery_coordinates.lon:
                        restaurant_distance = \
                            distance.distance((restaurant_coordinates.lat, restaurant_coordinates.lon),
                                              (delivery_coordinates.lat, delivery_coordinates.lon)).km
                        unsorted_restaurants[restaurant.name] = round(restaurant_distance, 2)
                    else:
                        unsorted_restaurants[restaurant.name] = '?'
            sorted_restaurants = dict(sorted(unsorted_restaurants.items(), key=lambda item: item[1]))
            restaurants_for_order = [f'{restaurant} - {sorted_restaurants[restaurant]} км'
                                     for restaurant in sorted_restaurants]
            record['restaurants'] = restaurants_for_order
        return orders_to_display


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        related_name='items',
        verbose_name="заказ",
        on_delete=models.CASCADE,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='товар',
    )

    quantity = models.IntegerField(
        'количество',
        db_index=True,
        validators=[
            MaxValueValidator(99),
            MinValueValidator(1)
        ],
    )

    product_fix_price = models.DecimalField(
        'фиксированная цена товара',
        db_index=True,
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
    )

    objects = OrderItemQuerySet.as_manager()

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f'{self.product.name} {self.order.lastname} {self.order.firstname}, {self.order.address}'
