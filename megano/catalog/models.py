from django.db import models
from django.db.models import (
    CASCADE,
    PROTECT,
    BooleanField,
    CharField,
    DateField,
    DecimalField,
    FileField,
    ForeignKey,
    ImageField,
    JSONField,
    ManyToManyField,
    Model,
    PositiveIntegerField,
    TextField,
)
from django.utils.translation import gettext_lazy as _


def banner_image_directory_path(instance: "Banner", filename: str) -> str:
    return "banners/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Banner(Model):
    """
    Модель баннера на главной странице
    """

    class Meta:
        verbose_name_plural = _("Баннеры")
        verbose_name = _("Баннер")

    title = CharField(max_length=256, verbose_name=_("Заголовок"))
    text = TextField(null=False, blank=False, verbose_name=_("Текст"))
    link = CharField(max_length=256, verbose_name=_("Ссылка"))
    active = BooleanField(default=False, verbose_name=_("Активен"))
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=banner_image_directory_path,
        verbose_name=_("Изображение"),
    )

    def __str__(self):
        return self.title

    def __repr__(self):
        return repr(self.title)


def seller_image_directory_path(instance: "Seller", filename: str) -> str:
    return "sellers/seller_{pk}/avatar/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Seller(Model):
    class Meta:
        verbose_name = _("Продавец")
        verbose_name_plural = _("Продавцы")

    name = models.CharField(max_length=100, null=False, verbose_name=_("Имя"))
    description = models.TextField(null=False, blank=True, verbose_name=_("Описание"))
    phone = models.CharField(max_length=15, null=False, verbose_name=_("Телефон"))
    address = models.TextField(null=False, verbose_name=_("Адрес"))
    email = models.EmailField(max_length=254, verbose_name=_("E-mail адрес"))
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=seller_image_directory_path,
        verbose_name=_("Изображение"),
    )
    products = models.ManyToManyField(
        "Product",
        through="Stock",
        blank=True,
        related_name="sellers",
        verbose_name=_("Товары"),
    )

    def __str__(self):
        return f"Seller(id={self.pk}, name={self.name})"


def category_image_directory_path(instance: "Category", filename: str) -> str:
    return f"images/category/{filename}"


class Category(Model):
    title = CharField(max_length=200, db_index=True, verbose_name=_("Заголовок"))
    image = FileField(
        upload_to=category_image_directory_path,
        verbose_name=_("Изображение"),
        null=True,
        blank=True,
    )
    parent = ForeignKey(
        "self",
        verbose_name=_("Подкатегория"),
        on_delete=models.PROTECT,
        related_name="subcategories",
        null=True,
        blank=True,
    )
    sorted_index = PositiveIntegerField(default=0, verbose_name=_("Индекс сортировки"))

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")


class Tag(Model):
    name = CharField(max_length=128, verbose_name=_("Название"))

    class Meta:
        verbose_name = _("Тэг")
        verbose_name_plural = _("Тэги")

    def __str__(self):
        return f"{self.name}"


def product_image_directory_path(instance: "ProductImage", filename: str) -> str:
    dir_name = f"images/product/{filename}"
    return dir_name


def get_default_value_for_characteristics():
    return {
        "Модель": "",
        "Год релиза": "",
    }


class ProductImage(Model):
    image = ImageField(
        upload_to=product_image_directory_path, verbose_name=_("Изображение")
    )
    alt = CharField(max_length=200, null=False, blank=True, verbose_name=_("Описание"))

    class Meta:
        verbose_name = _("Изображение товара")
        verbose_name_plural = _("Изображения товара")

    def __str__(self):
        return f"{self.pk}"


class Product(Model):
    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")

    category = ForeignKey(
        Category,
        on_delete=PROTECT,
        related_name="products",
        verbose_name=_("Категория"),
    )
    tag = ManyToManyField(
        Tag, blank=True, related_name="products", verbose_name=_("Тэги")
    )
    avatar = ForeignKey(
        ProductImage,
        on_delete=CASCADE,
        related_name="product",
        blank=True,
        null=True,
        verbose_name=_("Аватар"),
    )
    image = ManyToManyField(
        ProductImage, related_name="products", blank=True, verbose_name=_("Изображения")
    )
    name = CharField(max_length=128, db_index=True, verbose_name=_("Название"))
    description = TextField(
        null=False, blank=True, db_index=True, verbose_name=_("Описание")
    )
    manufacturer = CharField(max_length=200, verbose_name=_("Производитель"))
    active = BooleanField(default=False, verbose_name=_("Активен"))
    limited_edition = BooleanField(default=False, verbose_name=_("Лимитированный"))
    preview = CharField(max_length=200, null=True, blank=True, verbose_name=_("Превью"))
    characteristics = JSONField(
        encoder=None,
        decoder=None,
        verbose_name=_("Характиристики"),
        blank=True,
        null=True,
        default=get_default_value_for_characteristics,
    )

    def description_short(self):
        return f"{self.description[:120]} ..."

    def __str__(self) -> str:
        return f"Product(pk={self.pk}, name={self.name!r})"


class Stock(Model):
    seller = ForeignKey(
        Seller, on_delete=CASCADE, related_name="stocks", verbose_name=_("Продавец")
    )
    product = ForeignKey(
        Product, on_delete=CASCADE, related_name="stocks", verbose_name=_("Продукт")
    )
    quantity = PositiveIntegerField(default=0, verbose_name=_("Количество"))
    quantity_sold = PositiveIntegerField(default=0, verbose_name=_("Число проданных"))
    price = DecimalField(max_digits=16, decimal_places=2, verbose_name=_("Цена"))
    create_date = DateField(
        auto_now_add=True, verbose_name=_("Дата создания"), null=True
    )
    free_shipping = BooleanField(default=False, verbose_name=_("Бесплатная доставка"))

    def __str__(self):
        return f"Stock(product={self.product}, seller={self.seller})"

    class Meta:
        verbose_name = _("Склад")
        verbose_name_plural = _("Склады")


class TypeAmount(models.TextChoices):
    PERCENT = "PER", "Процентная скидка"
    ABSOLUTE = "ABS", "Абсолютная скидка"


class Review(Model):
    class Meta:
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")

    text = TextField(null=False, blank=True, db_index=True, verbose_name=_("Текст"))
    created_at = DateField(auto_now=True, verbose_name="Дата создания")
    rating = DecimalField(
        null=True, blank=True, max_digits=3, decimal_places=2, verbose_name=_("Оценка")
    )
    profile = ForeignKey(
        "account.Profile",
        on_delete=CASCADE,
        related_name="reviews",
        verbose_name=_("Пользователь"),
    )
    product = ForeignKey(
        Product,
        on_delete=PROTECT,
        null=True,
        blank=True,
        related_name="reviews",
        verbose_name=_("Товар"),
    )
    is_valid = models.BooleanField(default=False, verbose_name="Валидный")

    def __str__(self):
        return f"Rating={self.rating}"


def sale_product_directory_path(instance: "SaleProduct", filename: str) -> str:
    dir_name = f"images/sales/{filename}"
    return dir_name


class SaleProduct(models.Model):
    class Meta:
        verbose_name = _("Скидка")
        verbose_name_plural = _("Скидки")

    title = models.CharField(max_length=128, db_index=True, verbose_name=_("Название"))
    description = models.TextField(
        null=False, blank=True, db_index=True, verbose_name=_("Описание")
    )
    promocode = models.UUIDField(
        null=False,
        blank=True,
        db_index=True,
        verbose_name=_("Промокод"),
        unique=True,
    )
    image = models.ImageField(
        upload_to=sale_product_directory_path, verbose_name=_("Изображение")
    )
    stocks = models.ManyToManyField(
        "Stock", blank=True, related_name="sales", verbose_name=_("Склады")
    )
    date_start = models.DateField(
        null=False, blank=True, db_index=True, verbose_name=_("Дата начала")
    )
    date_end = models.DateField(
        null=False, blank=True, db_index=True, verbose_name=_("Дата конца")
    )
    CHOICES = [
        ("percent", "Percent"),
        ("ruble", "Ruble"),
    ]
    sale_type = models.CharField(
        default="percent", max_length=10, choices=CHOICES, verbose_name=_("Тип скидки")
    )
    sale_count = models.PositiveIntegerField(default=0, verbose_name=_("Размер скидки"))

    def get_price(self, price):
        if self.sale_type == "percent":
            return price - (price / 100 * self.sale_count)
        return price - self.sale_count
