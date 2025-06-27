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


@method_decorator(
    ratelimit(key="user_or_ip", rate="20/m", method="GET", block=True), name="get"
)
@method_decorator(
    ratelimit(key="user_or_ip", rate="5/m", method="POST", block=True), name="post"
)
class ShortenerListCreateView(generics.ListCreateAPIView, RateLimitExceptionAPIHandler):
    """
    View to list all shorteners and create a new one.
    """

    queryset = Shortener.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            if self.request.data.get("is_private"):
                return PrivateShortenerSerializerCreator
            if self.request.data.get("has_password"):
                return PasswordProtectedShortenerSerializerCreator
            return ShortenerSerializerCreator
        return ShortenerSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        # Determine the correct serializer for each instance
        data = []
        for instance in page if page is not None else queryset:
            if instance.password:
                serializer = PasswordProtectedShortenerSerializer(instance)
            elif instance.access_token:
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

        # Return the appropriate serializer for the created instance
        if isinstance(instance, PrivateShortenerSerializerCreator):
            response_serializer = PrivateShortenerSerializer(instance)
        elif isinstance(instance, PasswordProtectedShortenerSerializerCreator):
            response_serializer = PasswordProtectedShortenerSerializer(instance)
        else:
            response_serializer = ShortenerSerializer(instance)

        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


@method_decorator(ratelimit(key="user_or_ip", rate="20/m"), name="dispatch")
class ShortenerRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView, RateLimitExceptionAPIHandler
):
    """
    View to retrieve, update, or delete a shortener instance.
    """

    queryset = Shortener.objects.all()
    lookup_field = "short_url"

    def get_serializer_class(self):
        instance = self.get_object()
        if instance.password:
            return PasswordProtectedShortenerSerializer
        elif instance.access_token:
            return PrivateShortenerSerializer
        return ShortenerSerializer


# --- Redirection View ---


@ratelimit(key="user_or_ip", rate="100/h")
@ratelimit(key="user_or_ip", rate="30/m")
def redirect_view(request, short_url: str):
    """
    Redirects the user to the long URL associated with the short URL.
    Handles private (token-based) and password-protected URLs.
    """
    shortener = get_object_or_404(Shortener, short_url=short_url)

    # Handle private URLs (token-based)
    if shortener.access_token and not shortener.password:
        token = request.GET.get("token")
        if str(shortener.access_token) != token:
            return render(
                request,
                "private_url_auth.html",
                {"short_url": short_url},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    # Handle password-protected URLs
    if shortener.password:
        session_key = f"password_authenticated_for_{short_url}"
        if not request.session.get(session_key):
            if request.method == "POST":
                password = request.POST.get("password", "")
                if shortener.check_password(password):
                    request.session[session_key] = True
                    # Redirect to the same URL using GET to process redirection
                    return redirect(request.path)
                else:
                    context = {
                        "short_url": short_url,
                        "error": "Invalid password. Please try again.",
                    }
                    return render(
                        request,
                        "password_protect_form.html",
                        context,
                        status=status.HTTP_403_FORBIDDEN,
                    )

            # For GET requests, show the password form
            return render(
                request, "password_protect_form.html", {"short_url": short_url}
            )

    # If all checks pass, perform the redirection
    shortener.times_followed += 1
    shortener.save(update_fields=["times_followed"])
    return redirect(shortener.long_url)
