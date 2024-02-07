from django.urls import path

from order.views import (
    OrderDetailView,
    OrderingView,
    PaymentView,
    PaymentWithPaymentMethodView,
)

app_name = "order"

urlpatterns = [
    path("ordering/", OrderingView.as_view(), name="ordering"),
    path("ordering/payment/<int:pk>/", PaymentView.as_view(), name="payment"),
    path(
        "ordering/payment_with_payment_method/<int:pk>/",
        PaymentWithPaymentMethodView.as_view(),
        name="payment_with_payment_method",
    ),
    path("<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
]
