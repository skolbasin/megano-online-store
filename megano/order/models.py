from django.db import models
from django.utils.translation import gettext_lazy as _

from account.models import Profile
from catalog.models import Stock


class OrderStatus(models.TextChoices):
    NOT_PAID = "NOT_PAID", "Не оплачен"
    PAID = "PAID", "Оплачен"
    IN_DELIVERY = "IN_DELIVERY", "В доставке"
    DELIVERED = "DELIVERED", "Доставлен"


class DeliveryMethod(models.TextChoices):
    DELIVERY = "DELIVERY", "Доставка"
    EXPRESS_DELIVERY = "EXPRESS_DELIVERY", "Экспресс доставка"


class PaymentMethod(models.TextChoices):
    CARD = "CARD", "Онлайн картой"
    SOMEONE_ACCOUNT = "SOMEONE_ACCOUNT", "Онлайн с чужого счета"


class Order(models.Model):
    """
    Модель заказов
    """

    profile = models.ForeignKey(
        Profile, verbose_name="Пользователь", on_delete=models.DO_NOTHING
    )
    delivery_address = models.TextField(verbose_name=_("Адрес доставки"))
    comment = models.TextField(
        blank=True, default=_("Нет комментария"), verbose_name=_("Комментарий")
    )
    price = models.DecimalField(
        default=0, max_digits=16, decimal_places=2, verbose_name=_("Стоимость")
    )
    created_date = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Дата создания")
    )
    delivery_method = models.TextField(
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.DELIVERY,
        verbose_name=_("Способ доставки"),
    )
    payment_method = models.TextField(
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD,
        verbose_name=_("Способ оплаты"),
    )
    pay_result = models.BooleanField(default=False, verbose_name=_("Статсус оплаты"))
    order_status = models.TextField(
        choices=OrderStatus.choices,
        default=OrderStatus.NOT_PAID,
        verbose_name=_("Статус заказа"),
    )
    payment_error = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("payment error"),
    )

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")


class OrderItemModel(models.Model):
    stock = models.ForeignKey(
        Stock,
        related_name="order_items",
        on_delete=models.CASCADE,
        verbose_name=_("Склад"),
    )
    order = models.ForeignKey(
        Order,
        related_name="order_items",
        on_delete=models.CASCADE,
        verbose_name=_("Заказ"),
    )
    count = models.PositiveIntegerField(default=0, verbose_name=_("Количество"))
    full_price = models.DecimalField(
        default=0, max_digits=16, decimal_places=2, verbose_name=_("Сумма")
    )

    class Meta:
        verbose_name = _("Order item")
        verbose_name_plural = _("Order items")
