from django.db import models
from django.core.exceptions import ValidationError
import uuid
import re


# Create your models here.


def validate_phone_number(phone):
    if not re.match(r'^09\d{9}$', phone):
        raise ValidationError('Enter a valid phone number')


class Customer(models.Model):
    id = models.CharField(default=uuid.uuid4, editable=False, primary_key=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11, unique=True, validators=[validate_phone_number])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
