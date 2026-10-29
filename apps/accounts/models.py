from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom user model supporting customer registration, profiles,
    and staff management.
    """
    phone_number = models.CharField(max_length=20, blank=True, help_text="Customer contact number")
    city = models.CharField(max_length=100, blank=True, help_text="Primary residential/installation city")
    address = models.TextField(blank=True, help_text="Full address for service and delivery")
    is_customer = models.BooleanField(default=True, help_text="Designates whether this user is an end customer.")

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        full = self.get_full_name()
        return f"{full} ({self.username})" if full else self.username
