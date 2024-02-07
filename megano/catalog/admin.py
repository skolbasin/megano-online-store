from django.contrib import admin

from account.models import Profile

from .models import (
    Banner,
    Category,
    Product,
    ProductImage,
    Review,
    SaleProduct,
    Seller,
    Stock,
    Tag,
)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    model = Banner
    search_fields = ["title"]
    list_display = ["id", "title", "active", "link"]


class SellerProfileInLine(admin.TabularInline):
    model = Profile


class SellerProductsInline(admin.TabularInline):
    model = Seller.products.through


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    inlines = [
        SellerProfileInLine,
        SellerProductsInline,
    ]

    list_display = (
        "pk",
        "name",
        "description",
        "phone",
        "address",
        "email",
        "image",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = (
        "name",
        "pk",
    )
    search_fields = ("name",)

    def get_queryset(self, request):
        return Seller.objects.prefetch_related("profiles")


class ImageProductInline(admin.TabularInline):
    model = Product.image.through


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ImageProductInline,
    ]

    list_display = (
        "pk",
        "name",
        "avatar",
        "description",
        "manufacturer",
        "characteristics",
        "active",
    )
    list_display_links = ("pk", "name")
    search_fields = ("name", "description")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "title",
        "parent",
    )
    list_display_links = "pk", "title"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("pk", "image", "alt")
    list_display_links = ("pk",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "name")
    list_display_links = ("pk", "name")
    search_fields = ("name",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("pk", "product", "text", "rating", "created_at", "profile")
    list_display_links = (
        "pk",
        "product",
    )
    search_fields = "text", "rating"


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "seller",
        "product",
        "quantity",
        "quantity_sold",
        "price",
        "create_date",
        "free_shipping",
    )
    list_display_links = (
        "pk",
        "seller",
        "product",
    )
    search_fields = "pk", "seller"


class StockInline(admin.TabularInline):
    model = SaleProduct.stocks.through


@admin.register(SaleProduct)
class SaleProductAdmin(admin.ModelAdmin):
    inlines = [
        StockInline,
    ]

    list_display = (
        "pk",
        "title",
        "description",
        "promocode",
        "image",
        "date_start",
        "date_end",
    )
    list_display_links = (
        "pk",
        "title",
    )
    search_fields = (
        "title",
        "description",
        "promocode",
        "date_start",
        "date_end",
    )
    ordering = (
        "pk",
        "title",
        "date_start",
        "date_end",
    )
