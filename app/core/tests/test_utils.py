from django.test import TestCase
from core.utils import generate_token


class UtilsTests(TestCase):
    def test_generate_token(self):
        self.assertTrue(generate_token())
