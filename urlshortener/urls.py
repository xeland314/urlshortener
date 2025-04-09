"""
URL configuration for urlshortener project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

SchemaView = get_schema_view(
    openapi.Info(
        title="URL SHORTENER API",
        default_version="v1",
        description="API for creating and managing shortened URLs.",
        terms_of_service="https://roadmap.sh/projects/url-shortening-service",
        contact=openapi.Contact(
            email="alexpila.314@gmail.com"
        ),
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
