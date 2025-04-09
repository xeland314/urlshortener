"""
Django settings for urlshortener project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    default="django-insecure-8*#$m821j!@hakh+v195*)7oj=+&a6zgi5=l8a8#_1tc$o*4-*",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = "PRODUCTION" not in os.environ

ALLOWED_HOSTS = []

EXTERNAL_ALLOWED_HOSTS: str = os.getenv("ALLOWED_HOSTS")
if EXTERNAL_ALLOWED_HOSTS:
    ALLOWED_HOSTS.extend(EXTERNAL_ALLOWED_HOSTS.split(","))

CORS_ORIGIN_WHITELIST = []

EXTERNAL_CORS_ORIGIN: str = os.getenv("CORS_ORIGIN_WHITELIST")
if EXTERNAL_CORS_ORIGIN:
    CORS_ORIGIN_WHITELIST.extend(EXTERNAL_CORS_ORIGIN.split(","))

CSRF_TRUSTED_ORIGINS = []

EXTERNAL_CSRF_TRUSTED_ORIGINS: str = os.getenv("CSRF_TRUSTED_ORIGINS")
if EXTERNAL_CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.extend(EXTERNAL_CSRF_TRUSTED_ORIGINS.split(","))

# Media config:
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "whitenoise.runserver_nostatic",
    "corsheaders",
    "rest_framework",
    "shortener",
    "django_ratelimit",
    "drf_yasg",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urlshortener.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Configuración de manejo de errores
HANDLER404 = "shortener.views.custom_404"

WSGI_APPLICATION = "urlshortener.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {"default": dj_database_url.config(default="sqlite:///db.sqlite3")}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_LOCATION", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
    "cache-for-ratelimiting": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_LOCATION", "redis://127.0.0.1:6379/2"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}

RATELIMIT_USE_CACHE = "cache-for-ratelimiting"

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
# This setting tells Django at which URL static files are going to be served to the user.
# Here, they well be accessible at your-domain.onrender.com/static/...
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# Following settings only make sense on production and may break development environments.
if not DEBUG:  # Tell Django to copy statics to the `staticfiles` directory
    # in your application directory on Render.
    # Turn on WhiteNoise storage backend that takes care of compressing static files
    # and creating unique names for each version so they can safely be cached forever.
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
