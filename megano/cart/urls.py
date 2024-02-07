from django.urls import path

from .views import CartDetailView, add_product, add_promocode, delete_product

app_name = "cart"

urlpatterns = [
    path("", CartDetailView.as_view(), name="cart_details"),
    path("add_product", add_product, name="add_to_cart"),
    path("delete_product/<int:stock_id>/", delete_product, name="delete_product"),
    path("add_promocode/", add_promocode, name="add_promocode"),
]
