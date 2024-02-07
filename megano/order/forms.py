from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from account.models import Profile
from order.models import DeliveryMethod, PaymentMethod

User = get_user_model()


class RegistrationFormWhenOrdering(forms.Form):
    username = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=20, required=False)
    email = forms.EmailField()
    password = forms.CharField(max_length=20)
    password2 = forms.CharField(max_length=20)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("User exists"), code="user_exists")

        return email

    def clean_password2(self):
        password = self.cleaned_data["password"]
        password2 = self.cleaned_data["password2"]

        if password != password2:
            raise ValidationError(_("Passwords didn't match"), code="invalid")

    def save_user(self):
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        user = User(
            username=self.cleaned_data["username"],
            email=email,
        )
        user.set_password(password)
        profile = Profile(user=user, phone=self.cleaned_data["phone"])
        user.save()
        profile.save()

        return email, password

    def _post_clean(self):
        super()._post_clean()

        password = self.cleaned_data.get("password")
        if password:
            try:
                password_validation.validate_password(password)
            except ValidationError as error:
                self.add_error("password", error)


class DeliveryAndPaymentMethodWhenOrderingForm(forms.Form):
    delivery_method = forms.ChoiceField(choices=DeliveryMethod.choices)
    city = forms.CharField()
    address = forms.CharField()
    payment_method = forms.ChoiceField(choices=PaymentMethod.choices)
    comment = forms.CharField(required=False)


class PaymentByCardForm(forms.Form):
    card_number = forms.CharField()


class PaymentByCardWithPaymentMethodForm(forms.Form):
    card_number = forms.CharField()
    payment_method = forms.ChoiceField(choices=PaymentMethod.choices)
