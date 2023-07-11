from django.contrib import admin
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from rest_framework.response import Response
from django.shortcuts import redirect

from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Order
from .models import OrderItem


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        'address',
        'firstname',
        'lastname',
        'phonenumber',
    ]
    list_display = [
        'status',
        'address',
        'firstname',
        'lastname',
        'phonenumber',
    ]
    list_filter = [
        'status',
    ]
    inlines = [
        OrderItemInline
    ]

    # переопределен метод сохранения заказа
    def save_formset(self, request, form, formset, change):

        order = form.save(commit=False)
        if order.selected_restaurant and order.status == 'Уточняется':
            order.status = 'Собирается'
        elif not order.selected_restaurant and order.status == 'Собирается':
            order.status = 'Уточняется'
        order.save()

        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if not instance.product_fix_price:  # если фиксированная цена не указана - она равна текущей
                instance.product_fix_price = instance.product.price
            if instance.product_fix_price < 0:
                return Response({'Цена не может быть отрицательной!'})
            instance.save()
        # formset.save_m2m()

    def response_change(self, request, obj):
        res = super().response_change(request, obj)
        if "link_back" in request.GET:
            return redirect(request.GET['link_back'])
        else:
            return res
