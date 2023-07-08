from django.contrib import admin

# Register your models here.
from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = [
        'address',
    ]

    # list_display = [
    #     'address',
    #     'lan',
    #     'lot',
    #     'updated_datetime',
    # ]
