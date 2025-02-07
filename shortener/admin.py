from django.contrib import admin
from .models import Shortener


# Register your models here.
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
            {"fields": ("created", "times_followed", "updated"), "classes": ("collapse",)},
        ),
    )
    ordering = ("-created",)
