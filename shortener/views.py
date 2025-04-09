from django.shortcuts import get_object_or_404, redirect, render
from django_ratelimit.decorators import ratelimit, Ratelimited
from django.utils.decorators import method_decorator

from rest_framework import generics, status
from rest_framework.response import Response

from .pagination import CustomPagination
from .models import Shortener
from .serializers import ShortenerSerializer, ShortenerSerializerCreator


class RateLimitExceptionAPIHandler(generics.GenericAPIView):
    def handle_exception(self, exc):
        if isinstance(exc, Ratelimited):
            return Response(
                {"detail": "Too many requests"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        return super().handle_exception(exc)


class ShortenerCreate(generics.ListCreateAPIView, RateLimitExceptionAPIHandler):
    queryset = Shortener.objects.all()
    serializer_class = ShortenerSerializerCreator
    pagination_class = CustomPagination

    @method_decorator(
        ratelimit(key="user_or_ip", rate="20/m", method=["GET"], block=True)
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ShortenerSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ShortenerSerializer(queryset, many=True)
        return Response(serializer.data)

    @method_decorator(
        ratelimit(key="user_or_ip", rate="5/m", method="POST", block=True)
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data_formatted = ShortenerSerializer(serializer.instance).data
        return Response(data_formatted, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator(
    ratelimit(key="user_or_ip", rate="20/m"),
    name="get",
)
@method_decorator(
    ratelimit(key="get:q", rate="10/m"),
    name="get",
)
@method_decorator(
    ratelimit(key="user_or_ip", rate="10/m"),
    name="put",
)
@method_decorator(
    ratelimit(key="user_or_ip", rate="10/m"),
    name="patch",
)
@method_decorator(
    ratelimit(key="user_or_ip", rate="10/m"),
    name="delete",
)
class ShortenerDetail(
    generics.RetrieveUpdateDestroyAPIView, RateLimitExceptionAPIHandler
):
    queryset = Shortener.objects.all()
    serializer_class = ShortenerSerializer

    def get_object(self):
        queryset = self.get_queryset()
        short_url = self.kwargs["short_url"]
        return get_object_or_404(queryset, short_url=short_url)


@ratelimit(key="user_or_ip", rate="100/h")
@ratelimit(key="user_or_ip", rate="30/m")
@ratelimit(key="user_or_ip", rate="1/s")
@ratelimit(key="get:q", rate="10/m")
def redirect_view(request, short_url):
    try:
        shortener = Shortener.objects.get(short_url=short_url)
        shortener.times_followed += 1
        shortener.save()
        return redirect(shortener.long_url)
    except Shortener.DoesNotExist:
        return render(request, "404.html", status=404)


def custom_404(request, exception):
    return render(request, "404.html", status=404)


def ratelimit_handler(request, exception):
    return render(request, "429.html", status=429)
