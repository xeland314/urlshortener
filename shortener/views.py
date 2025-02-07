from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import generics, status
from rest_framework.response import Response

from shortener.pagination import CustomPagination
from .models import Shortener
from .serializers import ShortenerSerializer, ShortenerSerializerCreator


class ShortenerCreate(generics.ListCreateAPIView):
    queryset = Shortener.objects.all()
    serializer_class = ShortenerSerializerCreator
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ShortenerSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ShortenerSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data_formatted = ShortenerSerializer(serializer.instance).data
        return Response(data_formatted, status=status.HTTP_201_CREATED, headers=headers)

class ShortenerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shortener.objects.all()
    serializer_class = ShortenerSerializer

    def get_object(self):
        queryset = self.get_queryset()
        short_url = self.kwargs['short_url']
        return get_object_or_404(queryset, short_url=short_url)


def redirect_view(request, short_url):
    try:
        shortener = Shortener.objects.get(short_url=short_url)
        shortener.times_followed += 1
        shortener.save()
        return redirect(shortener.long_url)
    except Shortener.DoesNotExist:
        return render(request, "404.html", status=404)

def custom_404(request, exception):
    return render(request, '404.html', status=404)
