# trash_pickups/models.py
from django.db import models
from django.contrib.auth.models import User
from donations.models import DonationDrive
from django.utils import timezone


class TrashPickup(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),         # Created by restaurant
        ("accepted", "Accepted"),       # Driver accepted
        ("in_progress", "In Progress"), # Driver currently picking up
        ("completed", "Completed"),     # Finished
        ("cancelled", "Cancelled"),     # Cancelled by user/admin
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="trash_pickups"
    )
    restaurant_name = models.CharField(max_length=255)
    pickup_address = models.CharField(max_length=255)
    waste_type = models.CharField(max_length=50)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    scheduled_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    # optional donation
    donation_drive = models.ForeignKey(
        DonationDrive,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trash_pickups"
    )

    # linked driver
    driver = models.ForeignKey(
        'drivers.Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_pickups'
    )

    def save(self, *args, **kwargs):
        # fallback: ensure restaurant_name always has value
        if not self.restaurant_name:
            self.restaurant_name = self.pickup_address
        super().save(*args, **kwargs)

    def __str__(self):
        driver_name = self.driver.full_name if self.driver else "Unassigned"
        return f"{self.restaurant_name} ({self.status}) - Driver: {driver_name}"


# 🎁 Voucher model
class Voucher(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    points_required = models.IntegerField()
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.points_required} pts"


# 🎟️ Reward Redemption
class RewardRedemption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} redeemed {self.voucher.name}"
