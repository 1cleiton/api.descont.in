import pycep_correios
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models

from app.settings import AVAILABLE_ZONE
from core.exceptions import InvalidZipCodeError, ZipCodeOutOfAvailableZone


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

        address = Address.objects.create(neighborhood=data['bairro'],
                                         zipcode=data['cep'],
                                         city=data['cidade'],
                                         street=data['logradouro'],
                                         region=data['uf'],
                                         complement=data['complemento'])

        client = Client.objects.create(user=user, address=address)
        return client


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


class Address(models.Model):
    """Address model for users, partners and companies."""
    neighborhood = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=8, null=True, blank=True)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    complement = models.CharField(max_length=255)
