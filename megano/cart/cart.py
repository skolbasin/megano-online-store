from django.conf import settings

from catalog.models import Product, SaleProduct, Stock


class Cart(object):
    def __init__(self, request):
        """
        Инициализируем корзину
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add_promocode(self, promocode):
        self.session["promocode"] = str(promocode)
        sale = SaleProduct.objects.get(promocode=promocode)
        stock_ids = sale.stocks.values_list("id", flat=True)
        for stock_id in stock_ids:
            stock_id = str(stock_id)
            if stock_id not in self.cart:
                continue
            temp = self.cart[stock_id]
            self.cart[stock_id]["price"] = str(
                sale.get_price(float(temp.get("old_price")))
            )

    def add(self, stock, quantity=1):
        """
        Добавить продукт в корзину или обновить его количество.
        """
        stock_id = str(stock.id)
        if stock_id not in self.cart:
            self.cart[stock_id] = {
                "quantity": 1,
                "old_price": str(stock.price),
                "price": str(stock.price),
            }
        else:
            self.cart[stock_id]["quantity"] += quantity
        promocode = self.session.get("promocode")

        if promocode:
            self.add_promocode(promocode)

        self.save()

    def save(self):
        # Обновление сессии cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, stock):
        """
        Удаление единицы товара из корзины.
        """
        stock_id = str(stock.id)
        if self.cart[stock_id]["quantity"] == 1:
            del self.cart[str(stock_id)]
            self.save()
        else:
            self.cart[stock_id]["quantity"] -= 1
            self.save()

    def remove_all(self, stock_id):
        """
        Удаление товара из корзины.
        """
        del self.cart[str(stock_id)]
        self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        stock_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        stocks = Stock.objects.filter(id__in=stock_ids)
        for stock in stocks:
            self.cart[str(stock.id)]["product_id"] = stock.product.id
            self.cart[str(stock.id)]["seller"] = stock.seller.name

        for stock_id, item in self.cart.items():
            item["total_price"] = item["price"] * item["quantity"]
            item["id"] = stock_id

            yield item

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        return sum(
            float(item["price"]) * float(item["quantity"])
            for item in self.cart.values()
        )

    def clear(self):
        """
        Удаление корзины из сессии
        """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
