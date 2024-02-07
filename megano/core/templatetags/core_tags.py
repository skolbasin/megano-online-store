from django import template

from cart.cart import Cart
from catalog.models import Category
from catalog.services import ComparedProducts

register = template.Library()


@register.simple_tag()
def get_categories():
    return Category.objects.filter(parent__isnull=True).order_by("-sorted_index").all()


@register.simple_tag(takes_context=True, name="cart")
def get_cart(context):
    request = context["request"]
    cart = Cart(request)
    return cart


@register.simple_tag(takes_context=True, name="comparison_len")
def get_comparison_len(context):
    request = context["request"]
    comparison = ComparedProducts(request)
    comparison_len = comparison.__len__()
    return comparison_len
