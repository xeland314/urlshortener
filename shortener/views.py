from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Shortener
from .pagination import CustomPagination
from .serializers import (
    PasswordProtectedShortenerSerializer,
    PasswordProtectedShortenerSerializerCreator,
    PrivateShortenerSerializer,
    PrivateShortenerSerializerCreator,
    ShortenerSerializer,
    ShortenerSerializerCreator,
)
from .handlers import RateLimitExceptionAPIHandler


# --- API Views ---

@method_decorator(ratelimit(key="user_or_ip", rate="20/m", method="GET", block=True), name='get')
@method_decorator(ratelimit(key="user_or_ip", rate="5/m", method="POST", block=True), name='post')
class ShortenerListCreateView(generics.ListCreateAPIView, RateLimitExceptionAPIHandler):
    queryset = Shortener.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            if self.request.data.get("is_private"):
                return PrivateShortenerSerializerCreator
            if self.request.data.get("has_password"):
                return PasswordProtectedShortenerSerializerCreator
            return ShortenerSerializerCreator
        return ShortenerSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        data = []
        for instance in (page if page is not None else queryset):
            short_url = instance.short_url
            if short_url.startswith("pw") and len(short_url) == 9:
                serializer = PasswordProtectedShortenerSerializer(instance)
            elif short_url.startswith("p") and len(short_url) == 8:
                serializer = PrivateShortenerSerializer(instance)
            else:
                serializer = ShortenerSerializer(instance)
            data.append(serializer.data)
        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = ShortenerSerializer(instance)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator(ratelimit(key="user_or_ip", rate="20/m"), name="dispatch")
class ShortenerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView, RateLimitExceptionAPIHandler):
    queryset = Shortener.objects.all()
    lookup_field = "short_url"

    def get_serializer_class(self):
        instance = self.get_object()
        short_url = instance.short_url
        if self.request.method in ('PUT', 'PATCH'):
            return ShortenerSerializerCreator
        if short_url.startswith("pw") and len(short_url) == 9:
            return PasswordProtectedShortenerSerializer
        if short_url.startswith("p") and len(short_url) == 8:
            return PrivateShortenerSerializer
        return ShortenerSerializer


# --- Redirection View ---

@ratelimit(key="user_or_ip", rate="100/h")
@ratelimit(key="user_or_ip", rate="30/m")
def redirect_view(request, short_url: str):
    shortener = get_object_or_404(Shortener, short_url=short_url)

    if short_url.startswith("p") and len(short_url) == 8:
        token = request.GET.get("token")
        if str(shortener.access_token) != token:
            return render(request, "private_url_auth.html", {"short_url": short_url}, status=status.HTTP_401_UNAUTHORIZED)

    elif short_url.startswith("pw") and len(short_url) == 9:
        session_key = f"password_authenticated_for_{short_url}"
        if not request.session.get(session_key):
            if request.method == "POST":
                password = request.POST.get("password", "")
                if shortener.check_password(password):
                    request.session[session_key] = True
                    shortener.times_followed += 1
                    shortener.save(update_fields=['times_followed'])
                    return redirect(shortener.long_url)
                else:
                    context = {"short_url": short_url, "error": "Invalid password. Please try again."}
                    return render(request, "password_protect_form.html", context, status=status.HTTP_403_FORBIDDEN)
            return render(request, "password_protect_form.html", {"short_url": short_url}, status=status.HTTP_401_UNAUTHORIZED)

    shortener.times_followed += 1
    shortener.save(update_fields=['times_followed'])
    return redirect(shortener.long_url)
