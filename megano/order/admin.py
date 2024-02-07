from django.contrib import admin

from order.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ["profile", "delivery_method", "order_status"]
    list_display = [
        "pk",
        "user_verbose",
        "delivery_address",
        "comment",
        "price",
        "created_date",
        "delivery_method",
        "payment_method",
    ]
    list_display_links = ("pk",)

    def get_queryset(self, request):
        return Order.objects.select_related("profile")

    def user_verbose(self, obj: Order) -> str:
        return obj.profile.user.first_name or obj.profile.user.username
