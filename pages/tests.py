# pages/tests.py
from django.test import SimpleTestCase


class SimpleTests(SimpleTestCase):
    def test_home_page_status_code(self):
        for path in ['/', '/login/']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
