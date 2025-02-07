from django.urls import path
from .views import ShortenerCreate, ShortenerDetail, redirect_view

urlpatterns = [
    path("shorten/", ShortenerCreate.as_view(), name="shortener-create"),
    path(
        "shorten/<str:short_url>/", ShortenerDetail.as_view(), name="shortener-detail"
    ),
    path("<str:short_url>/", redirect_view, name="redirect"),
]
