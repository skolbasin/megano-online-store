from django.conf import settings
from django.db.models import Min

from catalog.models import Product


class ComparedProducts(object):
    """
    Класс для сервиса сравнения товаров с использованием сессий

    comparison: list[Product]

    При итерации возвращает объекты Product
    """

    def __init__(self, request):
        """
        Инициализируем объекты сравнения
        """
        self.session = request.session
        comparison = self.session.get(settings.COMPARISON_SESSION_ID)
        if not comparison:
            comparison = self.session[settings.COMPARISON_SESSION_ID] = list()
        self.comparison = comparison

    def __iter__(self):
        """
        Перебор продуктов в сессии сравнения.
        """
        product_ids = self.comparison
        for product_id in product_ids:
            product = Product.objects.get(id=product_id)
            price = product.stocks.aggregate(Min("price"))["price__min"]
            if price is None:
                price = 100
            yield product, price

    def add(self, product_id: int):
        """
        Добавление продукта в сессию сравнения.
        """
        product_id = str(product_id)
        if product_id not in self.comparison:
            if len(self.comparison) < 4:
                self.comparison.append(product_id)
        self.save()

    def save(self):
        """
        Обновление сессии
        """
        self.session[settings.COMPARISON_SESSION_ID] = self.comparison
        self.session.modified = True

    def remove(self, product_id: int):
        """
        Удаление товара из сессии сравнения.
        """
        product_id = str(product_id)
        self.comparison.remove(product_id)
        self.save()

    def clear(self):
        """
        Удаление элементов сессии сравнения
        """
        del self.session[settings.COMPARISON_SESSION_ID]
        self.session.modified = True

    def is_product_in_list(
        self,
        product_id,
    ):
        product_id = str(product_id)

        if product_id in self.comparison:
            return True
        return False

    def __len__(self):
        """
        Подсчет всех товаров в сессии сравнения.
        """
        return len(self.comparison)
