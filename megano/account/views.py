from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import FormView, View

from account.forms import (
    ForgotPasswordForm,
    ProfileChangeForm,
    RegistrationForm,
    UserChangeFormProfile,
)
from catalog.browsing_history import BrowsingHistory


class RegisterView(FormView):
    template_name = "registr.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("account:profile")

    def form_valid(self, form):
        response = super().form_valid(form)

        form.save()

        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")

        user = authenticate(self.request, username=email, password=password)
        login(self.request, user=user)

        return response

    def get_success_url(self):
        return self.success_url


class ProfileView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("/")
        user_name = request.user.username
        phone_number = request.user.profile.phone
        return render(
            request,
            "profile.html",
            {"user_name": user_name, "phone_formatted": phone_number},
        )

    def post(self, request, *args, **kwargs):
        user_name = request.user.username
        phone_number = request.user.profile.phone

        form_profile = ProfileChangeForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        form_user = UserChangeFormProfile(request.POST, instance=request.user)

        if form_profile.is_valid() and form_user.is_valid():
            form_profile.save(commit=False)
            form_profile.save()
            form_user.save()
            return render(
                request,
                "profile.html",
                {
                    "user_name": user_name,
                    "phone_formatted": phone_number,
                    "form_profile": form_profile,
                    "text_save": _("Профиль успешно сохранен"),
                },
            )

        return render(
            request,
            "profile.html",
            {
                "user_name": user_name,
                "phone_formatted": phone_number,
                "form_profile": form_profile,
                "form_user": form_user,
            },
        )


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    form_class = ForgotPasswordForm
    template_name = "e-mail.html"
    success_url = reverse_lazy("account:password_reset")
    success_message = _(
        "Письмо с инструкцией по восстановлению пароля отправлена на ваш email!"
    )
    email_template_name = "password_reset_email.html"


class ProfileOrderHistoryView(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect("/")

        orders = request.user.profile.order_set.all()

        return render(request, "historyorder.html", context={"orders": orders})


class AccountView(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        browsing_history = BrowsingHistory(request)
        if not request.user.is_authenticated:
            return redirect("/")
        last_order = request.user.profile.order_set.last()
        return render(
            request,
            "account.html",
            context={"browsing_history": browsing_history, "last_order": last_order},
        )


class ProfileBrowsingHistoryView(View):
    """
    История просмотров
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        browsing_history = BrowsingHistory(request)
        if not request.user.is_authenticated:
            return redirect("/")
        return render(
            request,
            "browsing_history.html",
            context={"browsing_history": browsing_history},
        )
