from django.contrib.auth.models import User
import uuid
from django.contrib.auth.hashers import check_password as django_check_password
from django.db import models
from django.utils import timezone
from .utils import create_shortened_url


class Shortener(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    times_followed = models.PositiveIntegerField(default=0)
    long_url = models.URLField()
    short_url = models.CharField(max_length=15, unique=True, blank=True)
    access_token = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, null=True, blank=True
    )
    password = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.long_url} to {self.short_url}"

    def save(self, *args, **kwargs):
        # Check if the long_url has changed
        if self.pk:
            orig = Shortener.objects.get(pk=self.pk)
            if orig.long_url != self.long_url:
                self.updated = timezone.now()
        if not self.short_url:
            self.short_url = create_shortened_url(self)
        super().save(*args, **kwargs)

        # Schedule Celery task if expires_at is set
        if self.expires_at:
            from .tasks import expire_shortener_url
            expire_shortener_url.apply_async((self.id,), eta=self.expires_at)


    def check_password(self, raw_password):
        """
        Verifica si la contraseña proporcionada coincide con la contraseña almacenada.
        """
        if not self.password:
            return False  # No hay contraseña almacenada
        return django_check_password(raw_password, self.password)


class PrivateShortener(Shortener):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = create_shortened_url(self, prefix="p")
        if not self.access_token:
            self.access_token = uuid.uuid4()
        super().save(*args, **kwargs)


class PasswordProtectedShortener(Shortener):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = create_shortened_url(self, prefix="pw")
        super().save(*args, **kwargs)
