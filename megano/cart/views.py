from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.http import require_POST

from catalog.models import Product, SaleProduct, Stock

from .cart import Cart


class CartDetailView(View):
    """View для корзины, реализация методов get, post и delete"""

    def get_cart_items(self, cart):
        cart_items = []
        for item in cart:
            product_id = item.get("product_id")
            if not product_id:
                continue
            product = Product.objects.get(id=product_id)

            cart_items.append(
                {
                    "id": item.get("id"),
                    "name": product.name,
                    "price": float(item["price"]),
                    "count": item["quantity"],
                    "seller": item["seller"],
                    "description": str(product.description[:150] + "..."),
                    "images": [
                        {"src": image, "alt": image.alt}
                        for image in product.image.all()
                    ],
                    "avatar": product.avatar,
                }
            )
        return cart_items

    def get(self, request, **kwargs):
        cart = Cart(request)
        cart_items = self.get_cart_items(cart)
        total_price = cart.get_total_price()
        context = {
            "cart": cart,
            "cart_items": cart_items,
            "total_price": total_price,
            "promocode": request.session.get("promocode", ""),
            "promocode_error": request.session.get("promocode_error", ""),
        }
        return render(request, "cart.html", context=context)

    def post(self, request):
        stock_id = request.POST.get("id")
        quantity = int(request.POST.get("count"))

        try:
            stock = Stock.objects.get(id=stock_id)
        except Stock.DoesNotExist:
            return HttpResponse.status.HTTP_404_NOT_FOUND

        cart = Cart(request)
        if request.POST.get("delete"):
            cart.remove(stock)
            previous_page = request.META.get("HTTP_REFERER")
            return redirect(previous_page)
        else:
            cart.add(stock, quantity)
            previous_page = request.META.get("HTTP_REFERER")
            return redirect(previous_page)


@require_POST
def add_product(request):
    id = request.POST.get("stock_id")
    stock = Stock.objects.get(id=int(id))
    cart = Cart(request)
    cart.add(stock)
    previous_page = request.META.get("HTTP_REFERER")
    return redirect(previous_page)


def delete_product(request, stock_id):
    cart = Cart(request)
    cart.remove_all(stock_id)
    previous_page = request.META.get("HTTP_REFERER")
    return redirect(previous_page)


@require_POST
def add_promocode(request):
    promocode = request.POST.get("promocode")
    try:
        cart = Cart(request)
        sale = SaleProduct.objects.get(promocode=promocode)
        cart.add_promocode(promocode)
        request.session["promocode_error"] = ""
    except Exception:
        request.session["promocode_error"] = "Промокод не найден!"
        request.session["promocode"] = ""

    previous_page = request.META.get("HTTP_REFERER")
    return redirect(previous_page)
