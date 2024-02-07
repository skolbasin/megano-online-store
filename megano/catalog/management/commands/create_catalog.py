from django.core.management import BaseCommand, call_command

from catalog.models import Banner, Category, Product, ProductImage, Seller, Stock, Tag


class Command(BaseCommand):
    """
    Команда для наполнения БД приложения Catalog
    """

    def handle(self, *args, **options):
        self.stdout.write("Create product")
        call_command("loaddata", "catalog_fixtures")
        sellers = Seller.objects.all()
        catalogs = Category.objects.all()
        product_images = ProductImage.objects.all()
        tags = Tag.objects.all()
        products = Product.objects.all()
        stocks = Stock.objects.all()
        banners = Banner.objects.all()
        models = [sellers, catalogs, product_images, tags, products, stocks, banners]
        for model in models:
            for item in model:
                item.save()
                print(f"{item} is saved")
