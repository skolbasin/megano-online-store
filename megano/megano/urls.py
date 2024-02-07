from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from megano import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("catalog/", include("catalog.urls")),
    path("accounts/", include("account.urls")),
    path("cart/", include("cart.urls")),
    path("order/", include("order.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
