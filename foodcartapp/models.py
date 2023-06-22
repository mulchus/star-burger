from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


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
        blank=True,
        null=True,
        db_index=True,
        default='',
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.lastname} {self.firstname}, {self.address}, {self.phonenumber}'


class OrderItemQuerySet(models.QuerySet):
    def get_prices(self):
        return self.exclude(
            order__status__exact='Выполнен').prefetch_related(
            'order', 'product').values(
            'order__pk', 'order__status', 'order__lastname', 'order__firstname', 'order__address',
            'order__comment', 'order__phonenumber').annotate(
            total_price=Sum(F('product__price') * F('quantity')))


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
    )
    product_fix_price = models.DecimalField(
        'фиксированная цена товара',
        db_index=True,
        default=0,
        max_digits=5,
        decimal_places=2
    )

    objects = OrderItemQuerySet.as_manager()

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f'{self.product.name} {self.order.lastname} {self.order.firstname}, {self.order.address}'
