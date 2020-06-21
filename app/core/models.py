import re

import pycep_correios
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models

from app.settings import AVAILABLE_ZONE, INVITE_LIMIT
from app.tasks import send_invite
from core.exceptions import (InvalidEmailError, InvalidSenderError,
                             InvalidZipCodeError, InvitationLimitExceeded,
                             ZipCodeOutOfAvailableZone)
from core.utils import generate_token


class UserManager(BaseUserManager):
    def validate_zipcode(self, zipcode):
        """Validate zipcode and get address by zipcode."""
        if not zipcode:
            raise InvalidZipCodeError()

        try:
            address = pycep_correios.get_address_from_cep(zipcode)
            if address.get('bairro') not in AVAILABLE_ZONE:
                raise ZipCodeOutOfAvailableZone()
            return address
        except Exception as e:
            if type(e) == ZipCodeOutOfAvailableZone:
                raise ZipCodeOutOfAvailableZone()
            raise InvalidZipCodeError()

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user."""
        if not email:
            raise ValueError('O usuário deve ter um e-mail válido.')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_client(self, email, password, zipcode=None, **extra_fields):
        """Creates and saves a new client."""
        data = self.validate_zipcode(zipcode)
        user = self.create_user(email=email, password=password, **extra_fields)

        # should not use zipcode from data because has hiphen
        address = Address.objects.create(neighborhood=data['bairro'],
                                         zipcode=zipcode,
                                         city=data['cidade'],
                                         street=data['logradouro'],
                                         region=data['uf'],
                                         complement=data['complemento'])

        client = Client.objects.create(user=user, address=address)
        return client

    def create_invite(self, sender, to):
        if not isinstance(sender, Client):
            raise InvalidSenderError()
        if not sender:
            raise InvalidSenderError()
        if not to:
            raise InvalidEmailError()
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$",
                        to):
            raise InvalidEmailError()

        limit = Invite.objects.filter(sender=sender).count()
        if limit >= INVITE_LIMIT:
            raise InvitationLimitExceeded()

        invite = Invite.objects.create(sender=sender, to=to)
        send_invite.delay(sender.user.name, to)

        return invite


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that suppors using email instead of username."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Client(models.Model):
    """Client model that represents an payed client."""
    user = models.OneToOneField('User', null=False, on_delete=models.CASCADE)
    address = models.ForeignKey('Address',
                                null=False,
                                on_delete=models.CASCADE)


class Invite(models.Model):
    """Invite model that represents invites sended to new clients"""
    sender = models.ForeignKey('Client', null=False, on_delete=models.CASCADE)
    to = models.EmailField(max_length=255, null=False, unique=True)
    token = models.CharField(max_length=255)
    sended = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.token = generate_token()
        super(Invite, self).save(*args, **kwargs)


# class Partner(models.Model):
#     """Partner model that represents an user administrator for companies."""
#     user = models.OneToOneField('User', null=False, on_delete=models.CASCADE)
#     company = models.ForeignKey('Company',
#                                 null=False,
#                                 on_delete=models.CASCADE)

# class Company(models.Model):
#     name = models.CharField(max_length=255)
#     cnpj = models.CharField(max_length=14)
#     address = models.ForeignKey('Address',
#                                 null=False,
#                                 on_delete=models.CASCADE)
#     categories = models.ManyToManyField('CompanyCategory',
#                                         related_name='companies')

# class CompanyCategory(models.Model):
#     name = models.CharField(max_length=255)
#     slug = models.CharField(max_length=255)


class Address(models.Model):
    """Address model for users, partners and companies."""
    neighborhood = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=8)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    complement = models.CharField(max_length=255)
