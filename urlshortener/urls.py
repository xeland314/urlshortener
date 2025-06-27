from django.contrib import admin
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static

SchemaView = get_schema_view(
    openapi.Info(
        title="URL SHORTENER API",
        default_version="v1",
        description="API for creating and managing shortened URLs.",
        terms_of_service="https://roadmap.sh/projects/url-shortening-service",
        contact=openapi.Contact(email="alexpila.314@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("shortener.urls")),
    path(
        "docs/swagger<format>/",
        SchemaView.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "docs/swagger/",
        SchemaView.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "docs/redoc/", SchemaView.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
