from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView # Import APIView

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
from .permissions import IsOwnerOrAdmin

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView

import uuid
from django.contrib.auth.hashers import make_password


# Helper function to add type properties to shortener objects
def add_shortener_type_properties(shortener):
    shortener.is_private_type = shortener.short_url.startswith("p") and len(shortener.short_url) == 8
    shortener.is_password_protected_type = shortener.short_url.startswith("pw") and len(shortener.short_url) == 9
    return shortener


# --- API Views ---

@method_decorator(ratelimit(key="user_or_ip", rate="20/m", method="GET", block=True), name='get')
@method_decorator(ratelimit(key="user_or_ip", rate="5/m", method="POST", block=True), name='post')
class ShortenerListCreateView(generics.ListCreateAPIView, RateLimitExceptionAPIHandler):
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Shortener.objects.filter(is_active=True)
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        elif self.request.user.is_authenticated:
            return queryset.filter(user=self.request.user)
        return queryset.filter(user__isnull=True) # Only show public URLs if not logged in

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

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        context = {
            'short_url': instance.short_url,
            'access_token': instance.access_token if instance.short_url.startswith("p") else None,
            'request': request # Pass the request object to access build_absolute_uri
        }
        return render(request, 'shortener/shortened_result.html', context, status=status.HTTP_201_CREATED)


@method_decorator(ratelimit(key="user_or_ip", rate="20/m"), name="dispatch")
class ShortenerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView, RateLimitExceptionAPIHandler):
    queryset = Shortener.objects.filter(is_active=True)
    lookup_field = "short_url"
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        queryset = Shortener.objects.filter(is_active=True)
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        elif self.request.user.is_authenticated:
            return queryset.filter(user=self.request.user)
        return queryset.filter(user__isnull=True) # Only allow access to public URLs if not logged in

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


# --- Custom Action Views (for HTMX) ---

class ChangePasswordFormView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def get(self, request, short_url):
        shortener = get_object_or_404(Shortener.objects.filter(is_active=True), short_url=short_url)
        self.check_object_permissions(request, shortener)
        shortener = add_shortener_type_properties(shortener) # Add properties
        return render(request, 'shortener/password_change_form.html', {'shortener': shortener})

class ChangePasswordView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def patch(self, request, short_url):
        shortener = get_object_or_404(Shortener.objects.filter(is_active=True), short_url=short_url)
        self.check_object_permissions(request, shortener)
        password = request.data.get('password')
        if password:
            shortener.password = make_password(password)
            shortener.save()
            shortener = add_shortener_type_properties(shortener) # Add properties
            return render(request, 'shortener/shortener_card.html', {'shortener': shortener})
        return Response({'error': 'Password not provided'}, status=status.HTTP_400_BAD_REQUEST)

class RegenerateTokenView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def post(self, request, short_url):
        shortener = get_object_or_404(Shortener.objects.filter(is_active=True), short_url=short_url)
        self.check_object_permissions(request, shortener)
        shortener.access_token = uuid.uuid4()
        shortener.save()
        shortener = add_shortener_type_properties(shortener) # Add properties
        return render(request, 'shortener/shortener_card.html', {'shortener': shortener})

class GetShortenerCardView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def get(self, request, short_url):
        shortener = get_object_or_404(Shortener.objects.filter(is_active=True), short_url=short_url)
        self.check_object_permissions(request, shortener)
        shortener = add_shortener_type_properties(shortener) # Add properties
        return render(request, 'shortener/shortener_card.html', {'shortener': shortener})


# --- Redirection View ---

@csrf_exempt
@ratelimit(key="user_or_ip", rate="100/h")
@ratelimit(key="user_or_ip", rate="30/m")
def redirect_view(request, short_url: str):
    shortener = get_object_or_404(Shortener, short_url=short_url)

    if not shortener.is_active:
        return render(request, "404.html", status=status.HTTP_404_NOT_FOUND)

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

def index_view(request):
    shorteners = Shortener.objects.none()
    if request.user.is_authenticated:
        if request.user.is_staff:
            shorteners = Shortener.objects.all()
        else:
            shorteners = Shortener.objects.filter(user=request.user)
    
    # Add type properties to each shortener before passing to template
    shorteners = [add_shortener_type_properties(s) for s in shorteners]

    return render(request, 'shortener/index.html', {'shorteners': shorteners})

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'shortener/register.html'
    success_url = reverse_lazy('login')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'shortener/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')
