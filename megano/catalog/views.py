from django.core.cache import cache
from django.db.models import Max, Min, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, View

from cart.cart import Cart
from catalog.forms import ComparisonForm, ReviewForm
from catalog.models import Product, Review, Seller, Stock
from core.models import SiteSettings
from megano import settings

from .browsing_history import BrowsingHistory
from .models import SaleProduct
from .services import ComparedProducts
from .utils import generate_sort_param, matched_items_for_comparison_view, sort_convert


class ProductDetail(DetailView):
    model = Product
    context_object_name = "product"
    template_name = "product_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = str(self.get_object().id)
        images = context["product"].image.all()
        context["viewed"] = True
        context["in_comparison_list"] = ComparedProducts(
            self.request
        ).is_product_in_list(product_id)
        context["stocks"] = context["product"].stocks.all()
        if context["stocks"]:
            context["price"] = context["product"].stocks.aggregate(Min("price"))[
                "price__min"
            ]
            context["price_id"] = (
                context["product"].stocks.filter(price=context["price"]).first().pk
            )
        else:
            context["price_id"] = 1
        context["images"] = images
        context["reviews"] = context["product"].reviews.filter(is_valid=True)
        context["review_form"] = ReviewForm()
        return context

    def get(self, request, *args, **kwargs):
        history = BrowsingHistory(request)
        self.object = self.get_object()
        history.add(product_id=self.object.id)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


@require_POST
def review_add(request, pk):
    form = ReviewForm(request.POST)
    if form.is_valid():
        text = form.cleaned_data["text"]
        product = get_object_or_404(Product, id=pk)
        profile = request.user.profile
        Review.objects.create(text=text, product=product, profile=profile)
    return redirect("catalog:product_detail", pk=pk)


class CatalogListView(ListView):
    template_name = "catalog.html"
    paginate_by = 6
    model = Product
    context_object_name = "products"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        return {**context, **self.get_param()}

    def sort_queryset(self, queryset, sort):
        sort_convert(self.request.session, sort)
        return queryset.order_by(sort)

    def get_last_sort(self, session):
        for k, v in session["sort_catalog"].items():
            if v["style"]:
                return v["param"]

    def get_param(self):
        context = {}
        context["sellers"] = Seller.objects.all()
        if "sort_catalog" not in self.request.session:
            self.request.session["sort_catalog"] = generate_sort_param()
        context["sort"] = self.request.session["sort_catalog"]
        context["category_id"] = self.kwargs.get("pk")
        return context

    def get_queryset(self):
        category_id = self.kwargs.get("pk")
        cache_key = settings.PRODUCT_CACHE_KEY.format(category_id=category_id)
        queryset = cache.get(cache_key)
        if not queryset:
            queryset = (
                super(CatalogListView, self)
                .get_queryset()
                .filter(category__id=category_id, active=True)
                .annotate(
                    price=Min("stocks__price"),
                    quantity=Max("stocks__quantity"),
                    rating=Max("reviews__rating"),
                    date=Max("stocks__create_date"),
                )
            )
        settings_cache = SiteSettings.objects.get()
        cache.set(cache_key, queryset, settings_cache.cache_time)

        sort = self.request.GET.get("sort")
        if sort:
            sort_convert(self.request.session, sort)
            queryset = self.sort_queryset(queryset, sort)
        return queryset

    def post(self, request, *args, **kwargs):
        last_sort = self.get_last_sort(self.request.session)
        seller = request.POST.get("seller")
        have_check = request.POST.get("havecheck")
        free_shipping = request.POST.get("freecheck")
        price = request.POST.get("price")
        title = request.POST.get("title")

        products = self.get_queryset()
        # Далее фильтр по полученным параметрам
        if seller:
            products = products.filter(product__seller__name=seller)
        if price:
            price_min, price_max = price.split(";")
            products = products.filter(price__range=[price_min, price_max])
        if title:
            products = products.filter(name=title)
        if have_check:
            products = products.filter(active=True)
        if free_shipping:
            products = products.filter(product__free_shipping=True)
        if last_sort:
            products.order_by(last_sort)
        context = self.get_param()
        context["products"] = products
        return render(
            request,
            self.template_name,
            context,
        )


class SalesListView(ListView):
    template_name = "sales.html"
    paginate_by = 12
    model = SaleProduct
    context_object_name = "sales"


@require_POST
def add_product_to_comparison(request):
    id = request.POST.get("product_id")
    comparison = ComparedProducts(request)
    comparison.add(id)
    previous_page = request.META.get("HTTP_REFERER")
    return redirect(previous_page)


def clear_comparison(request):
    comparison = ComparedProducts(request)
    comparison.clear()
    previous_page = request.META.get("HTTP_REFERER")
    return redirect(previous_page)


class ComparisonView(View):
    def get(self, request, *args, **kwargs):
        comparison_list = ComparedProducts(request)
        matched_items, flag_not_matching = matched_items_for_comparison_view(
            comparison_list
        )

        return render(
            request,
            "comparison.html",
            {
                "comparison_list": comparison_list,
                "matched_items": matched_items,
                "flag_not_matching": flag_not_matching,
                "flag": True,
            },
        )

    def post(self, request, *args, **kwargs):
        comparison_list = ComparedProducts(request)
        matched_items, flag_not_matching = matched_items_for_comparison_view(
            comparison_list
        )
        form = ComparisonForm(request.POST)
        if form.is_valid():
            return render(
                request,
                "comparison.html",
                {
                    "comparison_list": comparison_list,
                    "matched_items": matched_items,
                    "flag_not_matching": flag_not_matching,
                    "flag": True,
                },
            )

        return render(
            request,
            "comparison.html",
            {
                "comparison_list": comparison_list,
                "matched_items": matched_items,
                "flag_not_matching": flag_not_matching,
                "flag": False,
            },
        )


class SellerDetailView(DetailView):
    model = Seller
    context_object_name = "seller"
    template_name = "seller_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = context["seller"]
        context["stocks"] = seller.stocks.all()
        top_stocks = (
            Stock.objects.filter(seller=seller)
            .annotate(total_quantity_sold=Sum("quantity_sold"))
            .order_by("-total_quantity_sold")[:10]
        )
        context["top_stocks"] = top_stocks

        return context


class SalesDetailView(DetailView):
    model = SaleProduct
    context_object_name = "sale"
    template_name = "sales_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale_id = str(self.get_object().id)
        return context


def add_sale_product(request, sale_id):
    cart = Cart(request)
    sale = get_object_or_404(SaleProduct, id=sale_id)
    stocks = sale.stocks.all()
    for stock in stocks:
        cart.add(stock)
    cart.add_promocode(str(sale.promocode))
    request.session["promocode_error"] = ""
    previous_page = request.META.get("HTTP_REFERER")
    return redirect(previous_page)
