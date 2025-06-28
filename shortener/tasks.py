from celery import shared_task
from django.utils import timezone


@shared_task
def expire_shortener_url(shortener_id):
    from .models import Shortener

    try:
        shortener = Shortener.objects.get(id=shortener_id)
        if shortener.expires_at and shortener.expires_at <= timezone.now():
            if shortener.user is None:  # Anonymous URL
                shortener.delete()  # Delete anonymous expired URLs
            else:  # User-owned URL
                shortener.is_active = False  # Deactivate user-owned expired URLs
                shortener.save(update_fields=['is_active'])
    except Shortener.DoesNotExist:
        pass
