# accounts/models.py
from django.db import models
from django.contrib.auth.models import User


class OwnerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="owner_profile"
    )

    restaurant_name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, blank=True, null=True)

    # ✅ Added coordinates for pickup creation
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    STATUS_CHOICES = [
        ("active", "Active"),
        ("disabled", "Disabled"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    def __str__(self):
        return f"{self.user.username} - {self.restaurant_name}"
