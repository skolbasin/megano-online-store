from json import loads

from django.conf import settings
from django.db import models
from django.db.models import BooleanField, Model, PositiveIntegerField
from django.utils.translation import gettext_lazy as _

from catalog.models import Product


class SiteSettings(Model):
    cache_active = BooleanField(default=False, verbose_name=_("Активный"))
    cache_time = PositiveIntegerField(
        default=60 * 60 * 24, verbose_name=_("Время кэша")
    )  # sec*min*hor
    cache_products_time = PositiveIntegerField(
        default=60 * 60, verbose_name=_("Время кэша для продуктов")
    )  # sec*min*hor

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        if not self.cache_active:
            self.cache_time = 0
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()

    @staticmethod
    def load_config():
        with open("core/config/config.json", "r") as cfg:
            data = loads(cfg.read())
            model = SiteSettings.objects.get()
            model.cache_active = data["cache_active"]
            model.cache_time = data["cache_time"]
            model.save()

    def __str__(self):
        return "Настройки сайта"

    class Meta:
        verbose_name = _("Настройки сайта")
        verbose_name_plural = _("Настройки сайта")


class DeliverySettings(Model):
    order_cost_limit = PositiveIntegerField(
        default=2000, verbose_name=_("order_cost_limit")
    )
    delivery_markup = PositiveIntegerField(
        default=200, verbose_name=_("delivery_markup")
    )
    express_delivery_cost = PositiveIntegerField(
        default=500, verbose_name=_("express_delivery_cost")
    )

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()

    @staticmethod
    def load_config():
        with open("core/config/config.json", "r") as cfg:
            data = loads(cfg.read())
            model = DeliverySettings.objects.get(pk=1)
            model.order_cost_limit = data["order_cost_limit"]
            model.delivery_markup = data["delivery_markup"]
            model.express_delivery_cost = data["express_delivery_cost"]
            model.save()

    def __str__(self):
        return "Настройки доставки"

    class Meta:
        verbose_name = _("Настройки доставки")
        verbose_name_plural = _("Настройки доставки")
