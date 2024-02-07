import os

from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from catalog.models import Seller


def validate_image(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    if filesize > 2 * 1024 * 1024:
        raise ValidationError(_("Максимальный вес файла 2 MB"))


def get_profile_avatar_path(instance: "Profile", filename: str) -> str:
    ext = os.path.splitext(filename)[1]
    return "avatars/{0}{1}".format(instance.user.email, ext)


def validate_my_field(value):
    if not 1 <= len(value.split()) <= 3:
        raise validators.ValidationError(_("Введите от 1 до 3 слов"))


class User(AbstractUser):
    class Meta:
        db_table = "auth_user"
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    email = models.EmailField(
        verbose_name=_("E-mail адрес"),
        unique=True,
    )
    surname = models.CharField(max_length=150, blank=True, verbose_name=_("Фамилия"))

    username = models.CharField(
        max_length=100,
        validators=[validate_my_field],
        verbose_name=_("Имя пользователя"),
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]


class Profile(models.Model):
    """Модель профиля пользователя"""

    class Meta:
        verbose_name = _("Профиль")
        verbose_name_plural = _("Профили")

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name=_("Пользователь")
    )
    phone = models.CharField(
        max_length=18,
        null=True,
        blank=True,
        unique=True,
        verbose_name=_("Телефон"),
        validators=[
            RegexValidator(
                r"^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$",
                message=("Номер телефона должен быть в формате +7 (999) 999-99-99"),
            )
        ],
    )
    avatar = models.ImageField(
        verbose_name=_("Аватар"),
        null=True,
        blank=True,
        upload_to=get_profile_avatar_path,
        validators=[validate_image],
    )
    seller = models.ForeignKey(
        Seller,
        null=True,
        blank=True,
        default=None,
        on_delete=models.PROTECT,
        related_name="profiles",
        verbose_name=_("Продавец"),
    )

    def __str__(self):
        return f"Profile(user={self.user})"
