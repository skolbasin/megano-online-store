import time

from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView

from account.models import Profile
from cart.cart import Cart
from order.forms import (
    DeliveryAndPaymentMethodWhenOrderingForm,
    PaymentByCardForm,
    PaymentByCardWithPaymentMethodForm,
    RegistrationFormWhenOrdering,
)
from order.models import Order
from order.utils.ordering import (
    current_order_from_cart,
    refactor_cart_to_product_items,
    result_from_payment_system,
)

from .tasks import payment

User = get_user_model()


class OrderDetailView(DetailView):
    """
    Представление для отображения деталей заказа
    """

    template_name = "order_detail.html"
    queryset = Order.objects.select_related("profile")
    context_object_name = "order"


class OrderingView(View):
    """
    Представление для процесса заказа
    """

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        product_items = refactor_cart_to_product_items(cart)
        full_price = cart.get_total_price()
        if not request.user.is_authenticated:
            return render(
                request,
                "ordering.html",
                {
                    "product_items": product_items,
                    "full_price": full_price,
                },
            )
        user_name = request.user.username
        phone_number = request.user.profile.phone
        email = request.user.email
        return render(
            request,
            "ordering.html",
            {
                "user_name": user_name,
                "email": email,
                "phone_formatted": phone_number,
                "product_items": product_items,
                "full_price": full_price,
            },
        )

    def post(self, request, *args, **kwargs):
        form_user = RegistrationFormWhenOrdering(request.POST)
        form_delivery_and_payment = DeliveryAndPaymentMethodWhenOrderingForm(
            request.POST
        )

        cart = Cart(request)
        if cart.get_total_price() == 0:
            return redirect("core:index")

        if form_delivery_and_payment.is_valid():
            user = request.user
            if not request.user.is_authenticated:
                if not form_user.is_valid():
                    return render(
                        request,
                        "ordering.html",
                        {
                            "form_user": form_user,
                            "form_delivery_and_payment": form_delivery_and_payment,
                        },
                    )
                if not User.objects.filter(email=form_user.cleaned_data.get("email")):
                    user = User.objects.create(
                        username=form_user.cleaned_data.get("username"),
                        email=form_user.cleaned_data.get("email"),
                        password=form_user.cleaned_data.get("password"),
                    )
                    Profile.objects.create(
                        phone=form_user.cleaned_data.get("phone"), user=user
                    )
                else:
                    user = authenticate(
                        email=form_user.cleaned_data.get("email"),
                        password=form_user.cleaned_data.get("password"),
                    )

            profile = user.profile
            delivery_method = form_delivery_and_payment.cleaned_data["delivery_method"]
            city = form_delivery_and_payment.cleaned_data["city"]
            address = form_delivery_and_payment.cleaned_data["address"]
            delivery_address = f"{city}, {address}"
            payment_method = form_delivery_and_payment.cleaned_data["payment_method"]
            comment = form_delivery_and_payment.cleaned_data["comment"]

            current_order: Order = current_order_from_cart(
                cart=cart,
                profile=profile,
                delivery_address=delivery_address,
                comment=comment,
                delivery_method=delivery_method,
                payment_method=payment_method,
            )

            return redirect("order:payment", current_order.pk)

        return render(
            request,
            "ordering.html",
            {
                "form_user": form_user,
                "form_delivery_and_payment": form_delivery_and_payment,
            },
        )


class PaymentView(View):
    def get(self, request, pk, *args, **kwargs):
        current_order: Order = Order.objects.get(pk=pk)
        if current_order.order_status == "NOT_PAID":
            return render(
                request,
                "payment.html",
                {
                    "pk": pk,
                    "current_order_payment": current_order.payment_method,
                    "message": "Ждём подтверждения оплаты платёжной системы",
                },
            )
        return render(
            request,
            "payment_result.html",
            {"current_order": current_order},
        )

    def post(self, request, pk, **kwargs):
        cart = Cart(request)
        form_payment_by_card = PaymentByCardForm(request.POST)
        current_order: Order = Order.objects.get(pk=pk)
        if current_order.order_status != "NOT_PAID":
            return render(
                request,
                "payment_result.html",
                {"current_order": current_order},
            )
        if form_payment_by_card.is_valid():
            card_number = form_payment_by_card.cleaned_data["card_number"]
            card_number = int(f"{card_number[0:4]}{card_number[5:9]}")
            if current_order.order_status != "NOT_PAID":
                return render(
                    request,
                    "payment_result.html",
                    {"current_order": current_order},
                )

            payment_result = payment.apply_async(
                args=(card_number,),
            )
            time.sleep(4)
            current_order = result_from_payment_system(
                cart, current_order, payment_result.result
            )
            current_order.save()
            if current_order.pay_result:
                return render(
                    request,
                    "payment_result.html",
                    {"current_order": current_order},
                )
            return render(
                request,
                "payment_result.html",
                {"current_order": current_order},
            )


class PaymentWithPaymentMethodView(View):
    """
    Представление для процесса оплаты
    """

    def get(self, request, pk, *args, **kwargs):
        current_order: Order = Order.objects.get(pk=pk)
        if current_order.order_status == "NOT_PAID":
            return render(
                request,
                "payment_with_payment_method.html",
                {
                    "pk": pk,
                    "message": "Ждём подтверждения оплаты платёжной системы",
                },
            )
        return render(
            request,
            "payment_result.html",
            {"current_order": current_order},
        )

    def post(self, request, pk, **kwargs):
        cart = Cart(request)
        form_payment_by_card_with_method = PaymentByCardWithPaymentMethodForm(
            request.POST
        )
        current_order: Order = Order.objects.get(pk=pk)
        if current_order.order_status != "NOT_PAID":
            return render(
                request,
                "payment_result.html",
                {"current_order": current_order},
            )
        if form_payment_by_card_with_method.is_valid():
            card_number = form_payment_by_card_with_method.cleaned_data["card_number"]
            card_number = int(f"{card_number[0:4]}{card_number[5:9]}")
            payment_method = form_payment_by_card_with_method.cleaned_data[
                "payment_method"
            ]
            current_order.payment_method = payment_method
            current_order.save()
            if current_order.order_status != "NOT_PAID":
                return render(
                    request,
                    "payment_result.html",
                    {"current_order": current_order},
                )

            payment_result = payment.apply_async(
                args=(card_number,),
            )
            time.sleep(4)
            current_order = result_from_payment_system(
                cart, current_order, payment_result.result
            )
            current_order.save()
            return render(
                request,
                "payment_result.html",
                {"current_order": current_order},
            )
