from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.forms import CharField, PasswordInput, ModelForm
from .models import Shortener, PrivateShortener, PasswordProtectedShortener


@admin.register(Shortener)
class ShortenerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created",
        "updated",
        "times_followed",
        "long_url",
        "short_url",
    )
    search_fields = ("long_url", "short_url")
    list_filter = ("created", "times_followed")
    date_hierarchy = "created"
    readonly_fields = ("created", "updated", "times_followed", "short_url")
    fieldsets = (
        (None, {"fields": ("long_url", "short_url")}),
        (
            "Read-Only Fields",
            {
                "fields": ("created", "times_followed", "updated"),
                "classes": ("collapse",),
            },
        ),
    )
    ordering = ("-created",)


@admin.register(PrivateShortener)
class PrivateShortenerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created",
        "updated",
        "times_followed",
        "long_url",
        "short_url",
        "access_token",
    )
    search_fields = ("long_url", "short_url", "access_token")
    list_filter = ("created", "times_followed")
    date_hierarchy = "created"
    readonly_fields = (
        "created",
        "updated",
        "times_followed",
        "short_url",
        "access_token",
    )
    fieldsets = (
        (None, {"fields": ("long_url",)}),
        ("Private Link Details", {"fields": ("short_url", "access_token")}),
        (
            "Read-Only Fields",
            {
                "fields": ("created", "times_followed", "updated"),
                "classes": ("collapse",),
            },
        ),
    )
    ordering = ("-created",)


class PasswordProtectedShortenerForm(ModelForm):
    password = CharField(
        widget=PasswordInput(),
        required=False,
        help_text="Enter a new password or leave blank to keep the existing one.",
    )

    class Meta:
        model = PasswordProtectedShortener
        fields = (
            "long_url",
            "password",
            "short_url",
        )  # Include short_url if you want it editable in admin

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data["password"]:
            instance.password = make_password(self.cleaned_data["password"])
        if commit:
            instance.save()
        return instance


@admin.register(PasswordProtectedShortener)
class PasswordProtectedShortenerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created",
        "updated",
        "times_followed",
        "long_url",
        "short_url",
        "has_password",  # Custom display to indicate if a password is set
    )
    search_fields = ("long_url", "short_url")
    list_filter = ("created", "times_followed")
    date_hierarchy = "created"
    readonly_fields = ("created", "updated", "times_followed", "short_url")
    fieldsets = (
        (None, {"fields": ("long_url", "password")}),
        ("Protected Link Details", {"fields": ("short_url",)}),
        (
            "Read-Only Fields",
            {
                "fields": ("created", "times_followed", "updated"),
                "classes": ("collapse",),
            },
        ),
    )
    ordering = ("-created",)
    form = PasswordProtectedShortenerForm

    def save_model(self, request, obj, form, change):
        if form.cleaned_data["password"]:
            obj.password = make_password(form.cleaned_data["password"])
        elif not change:  # If it's a new object and no password was set
            obj.password = None  # Or some other default behavior
        obj.save()

    def has_password(self, obj):
        return bool(obj.password)

    has_password.boolean = True
    has_password.short_description = "Has Password"
