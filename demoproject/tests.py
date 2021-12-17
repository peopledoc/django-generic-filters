# coding=utf8
"""Test suite for django-generic-filters."""
from demoproject.compat import reverse
from django.test import TestCase


class HomeViewTestCase(TestCase):
    """Test homepage."""

    def test_get(self):
        """Homepage returns HTTP 200."""
        home_url = reverse("home")
        response = self.client.get(home_url)
        self.assertEqual(response.status_code, 200)
