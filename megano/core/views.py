import datetime

from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg
from django.shortcuts import render
from django.views.generic import View

from catalog.models import Banner, Product, Stock
from core.models import SiteSettings


class Index(View):
    def get_top_products(self):
        return []

    def get_banner(self, cache_time):
        # 3 рандомных баннера
        banners_cache = cache.get(settings.BANNER_SESSION_ID)
        if not banners_cache:
            banners = Banner.objects.filter(active=True).order_by("?")[:3]
            cache.set(settings.BANNER_SESSION_ID, banners, cache_time)
        return banners

    def get_product_day(self, cache_time) -> Stock:
        """
        Функция возвращает товар дня
        """
        stock_product_day = cache.get(settings.BANNER_SESSION_ID)
        if not stock_product_day:
            stock_product_day = Stock.objects.order_by("?").first()
            cache.set(settings.BANNER_SESSION_ID, stock_product_day, cache_time)
        return stock_product_day

    def get_hot_offers(self, cache_time) -> Stock:
        """
        Функция возвращает товары из публикации "Горячие предложения"
        """
        hot_offers = cache.get(settings.BANNER_SESSION_ID)
        if not hot_offers:
            hot_offers = Stock.objects.order_by("quantity")[:3]

            cache.set(settings.BANNER_SESSION_ID, hot_offers, cache_time)
        return hot_offers

    def get_limited_editions(self, cache_time) -> Stock:
        """
        Функция возвращает товары из публикации "Ограниченный тираж"
        """
        limited_editions = cache.get(settings.BANNER_SESSION_ID)
        if not limited_editions:
            limited_editions = []
            stocks = Stock.objects.all()
            for stock in stocks:
                if stock.product.limited_edition:
                    limited_editions.append(stock)

            cache.set(settings.BANNER_SESSION_ID, limited_editions, cache_time)
        return limited_editions

    def get(self, request, *args, **kwargs):
        settings = SiteSettings.objects.get()
        banners = self.get_banner(settings.cache_time)

        stock_product_day = self.get_product_day(settings.cache_time)
        product_day = stock_product_day.product
        product_with_new_price = product_day.stocks.order_by("price").first()
        product_day_new_price = product_with_new_price.price
        today = datetime.datetime.now() + datetime.timedelta(days=2)
        today_formatted = today.strftime("%d.%m.%Y %H:%M")

        top_products_4 = Product.objects.annotate(price=Avg("stocks__price"))[:4]
        top_products_5_6 = Product.objects.annotate(price=Avg("stocks__price"))[5:9]

        hot_offers = self.get_hot_offers(settings.cache_time)

        limited_editions = self.get_limited_editions(settings.cache_time)

        context = {
            "active_sliders": banners,
            "product_day": stock_product_day,
            "today": today_formatted,
            "product_day_new_price": product_day_new_price,
            "top_products_4": top_products_4,
            "top_products_5_6": top_products_5_6,
            "limited_editions": limited_editions,
            "hot_offers": hot_offers,
        }
        return render(request, "index.html", context)
