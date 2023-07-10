from django.db import models
from django.utils import timezone


# Create your models here.
class Location(models.Model):

    address = models.CharField(
        'адрес',
        max_length=100,
        unique=True,
    )

    lat = models.FloatField(
        blank=True,
        null=True,
        verbose_name='широта',
        db_index=True,
    )

    lon = models.FloatField(
        blank=True,
        null=True,
        verbose_name='долгота',
        db_index=True,
    )

    updated_datetime = models.DateTimeField(
        'обновлены',
        default=timezone.now,
        db_index=True,
    )



