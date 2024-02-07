from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetConfirmView
from django.urls import path, reverse_lazy

from account.forms import LoginForm, NewPasswordForm
from account.views import (
    AccountView,
    ProfileBrowsingHistoryView,
    ProfileOrderHistoryView,
    ProfileView,
    RegisterView,
    UserForgotPasswordView,
)

app_name = "account"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            authentication_form=LoginForm,
            template_name="login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(
            template_name="index.html",
            next_page=reverse_lazy("account:login"),
        ),
        name="logout",
    ),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("account/", AccountView.as_view(), name="account"),
    path(
        "restore_account/email/",
        UserForgotPasswordView.as_view(),
        name="password_reset",
    ),
    path(
        "restore_account/new-password/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="password.html",
            form_class=NewPasswordForm,
            success_url=reverse_lazy("account:login"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "profile/orders_history/",
        ProfileOrderHistoryView.as_view(),
        name="orders_history",
    ),
    path(
        "profile/browsing_history/",
        ProfileBrowsingHistoryView.as_view(),
        name="browsing_history",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]
    )
