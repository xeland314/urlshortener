from django.urls import path
from .views import (
    ShortenerListCreateView,
    ShortenerRetrieveUpdateDestroyView,
    redirect_view,
)


urlpatterns = [
    path("shorten/", ShortenerListCreateView.as_view(), name="shortener-list-create"),
    path(
        "shorten/<str:short_url>/",
        ShortenerRetrieveUpdateDestroyView.as_view(),
        name="shortener-detail-update-destroy",
    ),
    path("<str:short_url>/", redirect_view, name="redirect"),
]
