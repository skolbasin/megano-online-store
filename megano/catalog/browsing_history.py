from django.http import HttpRequest

from catalog.models import Product
from megano import settings


class BrowsingHistory(object):
    """
    Класс истории просмотренных товаров с использованием сессий

    history: list[Product]

    При итерации возвращает объекты Product
    """

    def __init__(self, request: HttpRequest):
        """
        Инициализируем историю
        """
        self.session = request.session
        history = self.session.get(settings.BROWSING_HISTORY_SESSION_ID)
        if not history:
            history = self.session[settings.BROWSING_HISTORY_SESSION_ID] = list()
        self.history = history

    def add(self, product_id: int):
        """
        Добавление продукта в список просмотренных
        """
        product_id = str(product_id)

        if product_id not in self.history:
            if len(self.history) >= 20:
                self.history.pop(0)
                self.history.append(product_id)
            else:
                self.history.append(product_id)
        self.save()

    def save(self):
        """
        Обновление сессии
        """
        self.session[settings.BROWSING_HISTORY_SESSION_ID] = self.history
        self.session.modified = True

    def __iter__(self):
        """
        Перебор продуктов в истории просмотров
        """
        product_ids = self.history
        for product_id in product_ids:
            product = Product.objects.get(id=product_id)
            yield product

    def clear(self):
        """
        Удаление истории просмотров из сессии
        """
        del self.session[settings.BROWSING_HISTORY_SESSION_ID]
        self.session.modified = True
