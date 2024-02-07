from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from account.models import Profile

User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    pass
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["username", "email", "password1", "password2"],
            },
        )
    ]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "avatar",
        "phone",
        "seller",
    )
    ordering = (
        "pk",
        "user",
        "seller",
    )
    search_fields = "seller", "user"

    def get_queryset(self, request):
        return Profile.objects.select_related("user").select_related("seller")
