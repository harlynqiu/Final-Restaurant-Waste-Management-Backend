from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Driver(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("on_pickup", "On Pickup"),
        ("inactive", "Inactive"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="driver_profile")
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(
        max_length=50,
        choices=[
            ("motorcycle", "Motorcycle"),
            ("tricycle", "Tricycle"),
            ("van", "Van"),
        ],
    )
    plate_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    is_active = models.BooleanField(default=True)
    date_hired = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.full_name} ({self.vehicle_type})"


class DriverLocation(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="locations")
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.driver.full_name} @ ({self.latitude}, {self.longitude})"
