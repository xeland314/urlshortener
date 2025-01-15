from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import generics
from .models import Shortener
from .serializers import ShortenerSerializer


class ShortenerListCreate(generics.ListCreateAPIView):
    queryset = Shortener.objects.all()
    serializer_class = ShortenerSerializer


class ShortenerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shortener.objects.all()
    serializer_class = ShortenerSerializer


def redirect_view(request, short_url):
    try:
        shortener = Shortener.objects.get(short_url=short_url)
        shortener.times_followed += 1
        shortener.save()
        return redirect(shortener.long_url)
    except Shortener.DoesNotExist:
        return render(request, "404.html", status=404)
