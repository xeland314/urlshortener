from django.db import models
from django.utils import timezone
from .utils import create_shortened_url

class Shortener(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    times_followed = models.PositiveIntegerField(default=0)
    long_url = models.URLField()
    short_url = models.CharField(max_length=15, unique=True, blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f'{self.long_url} to {self.short_url}'

    def save(self, *args, **kwargs):
        # Check if the long_url has changed
        if self.pk:
            orig = Shortener.objects.get(pk=self.pk)
            if orig.long_url != self.long_url:
                self.updated = timezone.now()
        if not self.short_url:
            self.short_url = create_shortened_url(self)
        super().save(*args, **kwargs)
