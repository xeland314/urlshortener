from django.test import TestCase
from .models import Shortener

class ShortenerModelTests(TestCase):

    def test_create_shortener(self):
        shortener = Shortener.objects.create(long_url='https://example.com')
        self.assertIsNotNone(shortener.short_url)
        self.assertEqual(shortener.times_followed, 0)

    def test_follow_shortened_url(self):
        shortener = Shortener.objects.create(long_url='https://example.com')
        shortener.times_followed += 1
        shortener.save()
        self.assertEqual(shortener.times_followed, 1)
