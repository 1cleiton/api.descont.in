from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy

from core.exceptions import InvalidSenderError, InvitationLimitExceeded
from core.models import Invite


class UserModelTests(TestCase):
    def setUp(self):
        self.client = get_user_model().objects.create_client(
            email='client@descont.in',
            password='Testpass@123',
            zipcode='20941150')

    def test_create_invite_available(self):
        """Test valid invite created has token and is not expired."""
        invite = get_user_model().objects.create_invite(
            sender=self.client, to='neighbor@descont.in')

        self.assertTrue(invite)
        self.assertIsNotNone(invite.token)
        self.assertFalse(invite.expired)

    def test_create_invite_with_invalid_sender(self):
        """Test create invite with another user as sender."""
        with self.assertRaises(InvalidSenderError):
            get_user_model().objects.create_invite(sender=self.client.user,
                                                   to='neighbor@descont.in')

    def test_create_invite_without_sender(self):
        """Test create invite without sender."""
        with self.assertRaises(InvalidSenderError):
            get_user_model().objects.create_invite(sender=None,
                                                   to='neighbor@descont.in')

    def test_create_invite_limit_exceeded(self):
        """Test create invite without invites."""
        mommy.make(Invite, sender=self.client, _quantity=10)
        with self.assertRaises(InvitationLimitExceeded):
            get_user_model().objects.create_invite(sender=self.client,
                                                   to='neighbor@descont.in')

    def test_invite_was_added_to_queue(self):
        """Test if the task send_email was created after new invite created."""
        pass
