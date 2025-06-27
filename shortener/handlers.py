from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


def ratelimit_handler(request, exception):
    """
    Custom view to handle rate-limiting exceptions.
    """
    return render(request, "429.html", status=429)


def custom_404(request, exception):
    """
    Custom view for 404 Not Found errors.
    """
    return render(request, "404.html", status=404)


class RateLimitExceptionAPIHandler(APIView):
    """
    Custom handler for DRF views that are rate-limited.
    """

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            if "rate limit" in str(e).lower():
                return Response(
                    {"error": "Rate limit exceeded. Please try again later."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            raise e
