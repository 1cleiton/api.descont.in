from core.exceptions import InvalidZipCodeError, ZipCodeOutOfAvailableZone

from django.contrib.auth import get_user_model
from django.test import TestCase


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an valid email is successful. """
        email = 'user@descont.in'
        password = 'Testpass@123'
        user = get_user_model().objects.create_user(email=email,
                                                    password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_and_client_email_normalized(self):
        """Test the email for a new user is normalized."""
        user_email = 'user@DESCONT.IN'
        password = 'Testpass@123'
        client_email = 'client@DESCONT.IN'
        zipcode = '20941150'
        user = get_user_model().objects.create_user(email=user_email,
                                                    password=password)
        client = get_user_model().objects.create_client(email=client_email,
                                                        password=password,
                                                        zipcode=zipcode)

        self.assertEqual(user.email, user_email.lower())
        self.assertEqual(client.user.email, client_email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error."""
        password = 'Testpass@123'
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None, password=password)

    def test_new_client_valid_zipcode(self):
        """Test creating client with valid zipcode."""
        email = 'user@descont.in'
        password = 'Testpass@123'
        zipcode = '20941150'
        client = get_user_model().objects.create_client(email=email,
                                                        password=password,
                                                        zipcode=zipcode)

        self.assertEqual(client.user.email, email)
        self.assertNotEqual(client.user.password, password)

    def test_new_client_invalid_zipcode(self):
        """Test creating user with zipcode invalid."""
        email = 'user@descont.in'
        password = 'Testpass@123'
        invalid_zipcode = '99999999'
        with self.assertRaises(InvalidZipCodeError):
            get_user_model().objects.create_client(email=email,
                                                   password=password,
                                                   zipcode=invalid_zipcode)

    def test_new_client_without_zipcode(self):
        """Test creating user without zipcode"""
        email = 'user@descont.in'
        password = 'Testpass@123'
        with self.assertRaises(InvalidZipCodeError):
            get_user_model().objects.create_client(email=email,
                                                   password=password,
                                                   zipcode=None)

    def test_new_client_with_zipcode_out_of_available_range(self):
        """Test creating user from zipcode of other regions"""
        email = 'user@descont.in'
        password = 'Testpass@123'
        zipcode = '22060002'
        with self.assertRaises(ZipCodeOutOfAvailableZone):
            get_user_model().objects.create_client(email=email,
                                                   password=password,
                                                   zipcode=zipcode)
