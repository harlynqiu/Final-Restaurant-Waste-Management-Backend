# accounts/models.py
from django.db import models
from django.contrib.auth.models import User

class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="owner_profile")
    restaurant_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.restaurant_name} ({self.user.username})"
