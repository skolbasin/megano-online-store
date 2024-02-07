from django.urls import path

from catalog.views import (
    CatalogListView,
    ComparisonView,
    ProductDetail,
    SalesDetailView,
    SalesListView,
    SellerDetailView,
    add_product_to_comparison,
    add_sale_product,
    clear_comparison,
    review_add,
)

app_name = "catalog"

urlpatterns = [
    path("products/<int:pk>/", ProductDetail.as_view(), name="product_detail"),
    path("products/<int:pk>/reviews", review_add, name="review_add"),
    path("<int:pk>/", CatalogListView.as_view(), name="catalog"),
    path("sales/", SalesListView.as_view(), name="sales"),
    path("comparison/", ComparisonView.as_view(), name="comparison"),
    path("comparison/clear", clear_comparison, name="clear_comparison"),
    path(
        "add_product_to_comparison",
        add_product_to_comparison,
        name="add_product_to_comparison",
    ),
    path("seller/<int:pk>", SellerDetailView.as_view(), name="seller_detail"),
    path("sales/<int:pk>", SalesDetailView.as_view(), name="sales_detail"),
    path("add_sale_product/<int:sale_id>/", add_sale_product, name="add_sale_to_cart"),
]
