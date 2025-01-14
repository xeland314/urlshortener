from django.urls import path
from .views import ShortenerListCreate, ShortenerDetail, redirect_view

urlpatterns = [
    path('shorteners/', ShortenerListCreate.as_view(), name='shortener-list-create'),
    path('shorteners/<int:pk>/', ShortenerDetail.as_view(), name='shortener-detail'),
    path('<str:short_url>/', redirect_view, name='redirect'),
]
