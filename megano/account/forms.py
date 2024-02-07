from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserChangeForm,
    UserCreationForm,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, RegexValidator
from django.forms import ModelForm
from django.utils.translation import gettext as _

from account.models import Profile

User = get_user_model()


class RegistrationForm(ModelForm):
    class Meta:
        model = User
        fields = "username", "email", "password"
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "user-input",
                    "placeholder": "E-mail",
                    "id": "email",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "user-input",
                    "placeholder": "Имя",
                    "id": "username",
                }
            ),
            "password": forms.PasswordInput(
                attrs={
                    "placeholder": "Пароль",
                    "id": "password",
                }
            ),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        profile = Profile(user=user)

        if commit:
            user.save()
            profile.save()

            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user

    def _post_clean(self):
        super()._post_clean()

        password = self.cleaned_data.get("password")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password", error)


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["class"] = "user-input"
        self.fields["username"].widget.attrs["placeholder"] = "E-mail"
        self.fields["password"].widget.attrs["placeholder"] = "*********"


class ForgotPasswordForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {
                "class": "user-input",
                "autocomplete": "off",
                "placeholder": "E-mail",
            }
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not list(self.get_users(email)):
            raise ValidationError(_("There's no user with this e-mail address."))

        return email


class NewPasswordForm(forms.Form):
    """Форма для ввода нового пароля при восстановлении аккаунта"""

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "Пароль",
            },
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        password_validation.validate_password(password, self.user)
        return password

    def save(self, commit=True):
        password = self.cleaned_data["password"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", "phone"]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = "username", "email", "password"
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "user-input",
                    "placeholder": "E-mail",
                    "id": "email",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "user-input",
                    "placeholder": "Имя Фамилия Отчество",
                    "id": "username",
                    "help_text": _(
                        (
                            "Пожалуйста, введите ваше имя, фамилию и "
                            "отчество в формате 'Имя Фамилия Отчество'"
                        )
                    ),
                    "onchange": "this.setCustomValidity('')",
                }
            ),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        profile = Profile(user=user)

        if commit:
            user.save()
            profile.save()

            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user


class PasswordChangeForm(UserCreationForm):
    old_password = forms.CharField(label="Old password", widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="New password", widget=forms.PasswordInput)
    passwordReply = forms.CharField(
        label="New password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("old_password", "new_password1", "passwordReply")

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        passwordReply = self.cleaned_data.get("passwordReply")
        if new_password1 and passwordReply and new_password1 != passwordReply:
            raise forms.ValidationError("Passwords do not match")
        return passwordReply

    def save(self, commit=True):
        user = super(PasswordChangeForm, self).save(commit=False)
        user.set_password(self.cleaned_data["new_password1"])
        if commit:
            user.save()
        return user


class ProfileChangeForm(forms.ModelForm):
    avatar = forms.FileField(required=False)
    phone = forms.CharField(
        max_length=18,
        required=False,
        validators=[
            RegexValidator(
                r"^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$",
                message=("Номер телефона должен быть в формате +7 (999) 999-99-99"),
            )
        ],
    )

    class Meta:
        model = Profile
        fields = (
            "phone",
            "avatar",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].widget.attrs["class"] = "form-control"
        self.fields["avatar"].widget = forms.ClearableFileInput(
            attrs={"class": "form-control"}
        )


class UserChangeFormProfile(UserChangeForm):
    old_password = forms.CharField(
        label="Old password", widget=forms.PasswordInput, required=False
    )
    new_password1 = forms.CharField(
        label="New password", widget=forms.PasswordInput, required=False
    )
    new_password2 = forms.CharField(
        label="New password confirmation", widget=forms.PasswordInput, required=False
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "old_password",
            "new_password1",
            "new_password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["email"].widget.attrs["class"] = "form-control"
        self.fields["old_password"].widget.attrs["class"] = "form-control"
        self.fields["new_password1"].widget.attrs["class"] = "form-control"
        self.fields["new_password2"].widget.attrs["class"] = "form-control"
        for visible in self.visible_fields():
            if (
                visible.errors
            ):  # при наличии ошибки поля, добавляем css-класс и меняем title
                visible.field.widget.attrs["class"] = "form__input has-error"
                visible.field.widget.attrs["title"] = "".join(visible.errors)
            else:
                visible.field.widget.attrs["class"] = "form__input"

            visible.field.widget.attrs["required"] = True

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if len(name.split()) < 1 or len(name.split()) > 3:
            raise forms.ValidationError(
                "Name must be at least two words", code="invalid"
            )
        return name

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.instance.check_password(old_password) and old_password:
            raise forms.ValidationError(_("Старый пароль не верен"))
        return old_password

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get("new_password1")
        if new_password1:
            validate_password(new_password1, self.instance)
        return new_password1

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError(_("New passwords do not match"))
        return new_password2

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["new_password1"]:
            user.set_password(self.cleaned_data["new_password1"])
        if commit:
            user.save()
        return user
