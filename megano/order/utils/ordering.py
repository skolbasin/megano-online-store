from cart.cart import Cart
from catalog.models import Product, Stock
from core.models import DeliverySettings
from order.models import Order, OrderItemModel


def refactor_cart_to_product_items(cart: Cart) -> list[dict]:
    """
    Функция для преобразования корзины в список
    return:list: product_items = [{'product': Product, 'quanty': int, 'price': int}, ...]
    """
    product_items = []
    for item in cart:
        product_item = dict()
        product_item["product"] = Product.objects.get(id=item["product_id"])
        product_item["quantity"] = item["quantity"]
        product_item["price"] = int(item["price"][: len(item["price"]) - 3]) * int(
            product_item["quantity"]
        )
        product_items.append(product_item)
    return product_items


def current_order_from_cart(
    cart: Cart, profile, delivery_address, comment, delivery_method, payment_method
):
    """
    Функция для создания заказа из корзины
    return: Order: current_order
    """
    price = cart.get_total_price()
    stocks = []
    current_order = Order.objects.create(
        profile=profile,
        delivery_address=delivery_address,
        comment=comment,
        price=price,
        delivery_method=delivery_method,
        payment_method=payment_method,
    )
    current_order.save()

    for item in cart:
        full_price = item["total_price"]
        quantity = item["quantity"]
        stock = Stock.objects.get(id=item["id"])
        stocks.append(stock)

        current_order_item = OrderItemModel.objects.create(
            stock=stock,
            order=current_order,
            count=quantity,
            full_price=full_price,
        )
        current_order_item.save()

    stocks_count = len(set(stocks))
    delivery_settings: DeliverySettings = DeliverySettings.objects.get()
    if delivery_method == "EXPRESS_DELIVERY":
        current_order.price += delivery_settings.express_delivery_cost
    if delivery_method == "DELIVERY":
        if price < delivery_settings.order_cost_limit or stocks_count > 1:
            current_order.price += delivery_settings.delivery_markup
    current_order.save()
    return current_order


def result_from_payment_system(cart: Cart, order: Order, payment_result: list) -> Order:
    """
    Функция вывода результата системы оплаты
    return: Order
    """
    if payment_result[0]:
        order.payment_error = None
        order.order_status = "PAID"
        order.pay_result = True
        for item in order.order_items.all():
            item.stock.quantity -= 1
            item.stock.quantity_sold += 1
            item.stock.save()
        order.save()
        cart.clear()
    else:
        order.payment_error = payment_result[1]

    return order
