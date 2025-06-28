from django.urls import path
from .views import (
    ShortenerListCreateView,
    ShortenerRetrieveUpdateDestroyView,
    redirect_view,
    index_view,
    RegisterView,
    login_view,
    logout_view,
    ChangePasswordFormView,
    ChangePasswordView,
    RegenerateTokenView,
    GetShortenerCardView,
)


urlpatterns = [
    path("", index_view, name="home"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("shorten/", ShortenerListCreateView.as_view(), name="shortener-list-create"),
    path(
        "shorten/<str:short_url>/",
        ShortenerRetrieveUpdateDestroyView.as_view(),
        name="shortener-detail-update-destroy",
    ),
    path("<str:short_url>/", redirect_view, name="redirect"),
    path(
        "shorten/<str:short_url>/change-password-form/",
        ChangePasswordFormView.as_view(),
        name="shortener-change-password-form",
    ),
    path(
        "shorten/<str:short_url>/change-password/",
        ChangePasswordView.as_view(),
        name="shortener-change-password",
    ),
    path(
        "shorten/<str:short_url>/regenerate-token/",
        RegenerateTokenView.as_view(),
        name="shortener-regenerate-token",
    ),
    path(
        "shorten/<str:short_url>/get-card/",
        GetShortenerCardView.as_view(),
        name="shortener-get-card",
    ),
]
