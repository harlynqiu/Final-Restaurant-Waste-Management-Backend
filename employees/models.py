from django.db import models
from accounts.models import OwnerProfile

class Employee(models.Model):
    owner = models.ForeignKey(
        OwnerProfile,
        on_delete=models.CASCADE,
        related_name="employees"
    )

    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    restaurant_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=20, default="active")

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.restaurant_name})"
