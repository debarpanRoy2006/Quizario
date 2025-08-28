from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # By default, the email field in AbstractUser is not unique.
    # We are overriding it here to enforce uniqueness.
    email = models.EmailField(unique=True)

    # Your original custom field
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username
