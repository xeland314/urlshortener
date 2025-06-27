from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Shortener, PrivateShortener, PasswordProtectedShortener


class ShortenerModelTest(APITestCase):
    """
    Tests for the Shortener model and its proxies.
    """

    def test_create_public_shortener(self):
        s = Shortener.objects.create(long_url="https://www.google.com")
        self.assertFalse(s.short_url.startswith("p"))
        self.assertFalse(s.short_url.startswith("pw"))

    def test_create_private_shortener(self):
        s = PrivateShortener.objects.create(long_url="https://private.com")
        self.assertTrue(s.short_url.startswith("p"))

    def test_create_password_protected_shortener(self):
        s = PasswordProtectedShortener.objects.create(
            long_url="https://password.com", password=make_password("pass")
        )
        self.assertTrue(s.short_url.startswith("pw"))


class ShortenerAPITest(APITestCase):
    """
    Tests for the Shortener API endpoints.
    """

    def setUp(self):
        self.public = Shortener.objects.create(long_url="https://public.com")
        self.private = PrivateShortener.objects.create(long_url="https://private.com")
        self.password = PasswordProtectedShortener.objects.create(
            long_url="https://password.com", password=make_password("pass123")
        )

    def test_create_public_url(self):
        url = reverse("shortener-list-create")
        data = {"long_url": "https://example.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access_token", response.data)
        self.assertIn("long_url", response.data)

    def test_list_shorteners_hides_sensitive_urls(self):
        url = reverse("shortener-list-create")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 3)
        # Public URL should be visible
        self.assertIn(
            "long_url",
            next(r for r in results if r["short_url"] == self.public.short_url),
        )
        # Private and Password URLs should be hidden
        self.assertNotIn(
            "long_url",
            next(r for r in results if r["short_url"] == self.private.short_url),
        )
        self.assertNotIn(
            "long_url",
            next(r for r in results if r["short_url"] == self.password.short_url),
        )

    def test_retrieve_public_shortener(self):
        url = reverse(
            "shortener-detail-update-destroy",
            kwargs={"short_url": self.public.short_url},
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("long_url", response.data)

    def test_retrieve_private_shortener_hides_url(self):
        url = reverse(
            "shortener-detail-update-destroy",
            kwargs={"short_url": self.private.short_url},
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("long_url", response.data)

    def test_update_shortener(self):
        url = reverse(
            "shortener-detail-update-destroy",
            kwargs={"short_url": self.public.short_url},
        )
        new_url = "https://updated.com"
        data = {"long_url": new_url}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.public.refresh_from_db()
        self.assertEqual(self.public.long_url, new_url)


class RedirectViewTest(APITestCase):
    """
    Tests for the redirect_view logic.
    """

    def setUp(self):
        self.public = Shortener.objects.create(long_url="http://public.com")
        self.private = PrivateShortener.objects.create(long_url="http://private.com")
        self.password = PasswordProtectedShortener.objects.create(
            long_url="http://password.com", password=make_password("secret-pass")
        )

    def test_public_redirect(self):
        url = reverse("redirect", kwargs={"short_url": self.public.short_url})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, self.public.long_url)

    def test_private_redirect_success(self):
        url = reverse("redirect", kwargs={"short_url": self.private.short_url})
        token = self.private.access_token
        response = self.client.get(f"{url}?token={token}")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, self.private.long_url)

    def test_private_redirect_fail_no_token(self):
        url = reverse("redirect", kwargs={"short_url": self.private.short_url})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_redirect_flow(self):
        """Test the full password authentication and redirection flow."""
        url = reverse("redirect", kwargs={"short_url": self.password.short_url})

        # 1. First GET request should ask for password
        response_get1 = self.client.get(url)
        self.assertEqual(response_get1.status_code, status.HTTP_401_UNAUTHORIZED)

        # 2. POST with correct password should now redirect directly to the long URL
        response_post = self.client.post(url, {"password": "secret-pass"})
        self.assertEqual(response_post.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response_post.url, self.password.long_url)

        # 3. Verify that the session was set and a subsequent GET also works
        response_get2 = self.client.get(url)
        self.assertEqual(response_get2.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response_get2.url, self.password.long_url)
