# drivers/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Driver(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="driver_profile",
        null=True, blank=True  # ✅ allow admin to create drivers even if user not selected
    )
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    license_number = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=50, default="motorcycle")
    plate_number = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_hired = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        default="available",
        choices=[
            ("available", "Available"),
            ("on_pickup", "On Pickup"),
            ("inactive", "Inactive"),
        ],
    )
    total_completed_pickups = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.full_name} ({self.status})"


class DriverLocation(models.Model):
    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="locations"
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.driver.full_name} @ {self.latitude}, {self.longitude}"
