from core.exceptions import InvalidZipCodeError, ZipCodeOutOfAvailableZone

from django.contrib.auth import get_user_model
from django.test import TestCase


class ModelTests(TestCase):
    def setUp(self):
        self.password = 'Testpass@123'

        self.valid_email = 'user@descont.in'
        self.client_valid_email = 'client@descont.in'
        self.invalid_email = 'justastring.com'
        self.denormalized_email = 'user@DESCONT.IN'

        self.valid_zipcode = '20941150'
        self.invalid_zipcode = '99999'
        self.outzone_zipcode = '22060002'

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an valid email is successful. """
        user = get_user_model().objects.create_user(email=self.valid_email,
                                                    password=self.password)

        self.assertEqual(user.email, self.valid_email)
        self.assertTrue(user.check_password(self.password))

    def test_new_user_and_client_email_normalized(self):
        """Test the email for a new user is normalized."""
        user = get_user_model().objects.create_user(email=self.valid_email,
                                                    password=self.password)
        client = get_user_model().objects.create_client(
            email=self.client_valid_email,
            password=self.password,
            zipcode=self.valid_zipcode)

        self.assertEqual(user.email, self.valid_email.lower())
        self.assertEqual(client.user.email, self.client_valid_email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None,
                                                 password=self.password)

    def test_new_client_valid_zipcode(self):
        """Test creating client with valid zipcode."""
        client = get_user_model().objects.create_client(
            email=self.valid_email,
            password=self.password,
            zipcode=self.valid_zipcode)

        self.assertEqual(client.user.email, self.valid_email)
        self.assertNotEqual(client.user.password, self.password)
        self.assertTrue(client.user.check_password(self.password))

    def test_new_client_invalid_zipcode(self):
        """Test creating user with zipcode invalid."""
        with self.assertRaises(InvalidZipCodeError):
            get_user_model().objects.create_client(
                email=self.valid_email,
                password=self.password,
                zipcode=self.invalid_zipcode)

    def test_new_client_without_zipcode(self):
        """Test creating user without zipcode"""
        with self.assertRaises(InvalidZipCodeError):
            get_user_model().objects.create_client(email=self.valid_email,
                                                   password=self.password,
                                                   zipcode=None)

    def test_new_client_with_zipcode_out_of_available_range(self):
        """Test creating user from zipcode of other regions"""
        with self.assertRaises(ZipCodeOutOfAvailableZone):
            get_user_model().objects.create_client(
                email=self.valid_email,
                password=self.password,
                zipcode=self.outzone_zipcode)
